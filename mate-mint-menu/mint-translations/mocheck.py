#!/usr/bin/env python

import polib
import sys
import os
import subprocess
import thread
import time
import urllib
from gi.repository import Gtk, GObject, GLib, Pango, GdkPixbuf
GObject.threads_init()

ALLOWED = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
COMMON_DATE_TOKENS = "ABeHYDMSmyp"
COMMON_INT_TOKENS = ["d", "'d", "ld", "I"]
COMMON_STR_TOKENS = ["s", "B"]
COMMON_I_TOKENS = ["i", "li", "I"]
DATE_THRESHOLD = 2

MO_EXT = ".mo"
PO_EXT = ".po"

GOOD = 0
BAD_MISCOUNT = 1
BAD_MISMATCH = 2
BAD_UNESCAPED_QUOTE = 3

BAD_EXCLUSIONS = 80

BAD_MISCOUNT_MAYBE_DATE = 99
BAD_MISMATCH_MAYBE_DATE = 100

def allowed(char):
    return char in ALLOWED

def same_type(token1, token2):    
    if (token1[1:] in COMMON_INT_TOKENS and token2[1:] in COMMON_INT_TOKENS):
        return True
    if (token1[1:] in COMMON_STR_TOKENS and token2[1:] in COMMON_STR_TOKENS):
        return True
    if (token1[1:] in COMMON_I_TOKENS and token2[1:] in COMMON_I_TOKENS):
        return True
    return False

class TokenList(list):
    def __init__(self):
        list.__init__(self)
        self.used_indices = []

    def add(self, entry):
        position = -1
        if "$" in entry:
            position = entry[1:entry.find("$")]
            self.used_indices.append(position)
            entry = entry.replace("$", "")
            entry = entry.replace(position, "")
            position = int(position)
        if position == -1 or len(self) == 0 or position > len(self):
            self.append(entry)
        else:
            self.insert(position - 1, entry)

class Mo:
    def __init__(self, inst, locale, path):
        self.mofile = inst
        self.locale = locale
        self.path = path
        self.bad_entries = []
        self.current_index = 1

class ThreadedTreeView(Gtk.TreeView):
    def __init__(self, parent, t):
        Gtk.TreeView.__init__(self)
        self.type = t
        self.progress = parent.progress
        self.datecheck = parent.datecheck
        self.revert = parent.revert
        self.save = parent.save
        self.dirty = False
        self._count = 0
        self.set_rules_hint(True)
        column = Gtk.TreeViewColumn("Language", Gtk.CellRendererText(), markup=2)
        self.append_column(column)

        cr = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("MsgId", cr, markup=3)
        cr.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
        cr.set_property('wrap-width', 450)
        self.append_column(column)

        cr = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("MsgStr", cr, markup=4)
        column.set_expand(True)
        cr.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
        cr.set_property('wrap-width', 450)
        cr.set_property('editable', True)

        cr.connect("edited", self.on_cell_edited)
        self.append_column(column)

        cr = Gtk.CellRendererPixbuf()
        column = Gtk.TreeViewColumn("Dirty", cr, pixbuf=6)
        column.set_cell_data_func(cr, self.dirty_pixbuf_func)
        column.set_max_width(50)
        self.append_column(column)

        self._loading_queue = []
        self._loading_queue_lock = thread.allocate_lock()

        self._loading_lock = thread.allocate_lock()
        self._loading = False

        self._loaded_data = []
        self._loaded_data_lock = thread.allocate_lock()

    def on_cell_edited(self, renderer, path, new_text):
        self.model[path][4] = new_text
        self.model[path][5] = new_text != self.model[path][1].msgstr.encode('utf-8')
        self.update_buttons()

    def dirty_pixbuf_func(self, col, cell, model, iter, data):
        dirty = model.get_value(iter, 5)
        if dirty:
            if self.check_entry(model.get_value(iter, 1), model.get_value(iter, 4)) == GOOD:
                cell.set_property("stock-id", "gtk-yes")
            else:
                cell.set_property("stock-id", "gtk-no")
        else:
            cell.set_property("stock-id", None)

    def update_buttons(self):
        self.dirty = False
        dirty_iter = self.model.get_iter_first()
        while dirty_iter != None:
            dirty = self.model.get_value(dirty_iter, 5)
            if dirty:
                self.dirty = True
            dirty_iter = self.model.iter_next(dirty_iter)
        self.save.set_sensitive(self.dirty)
        self.revert.set_sensitive(self.dirty)

    def save_changes(self):
        iter = self.model.get_iter_first()
        while iter != None:
            if self.model.get_value(iter, 5):
                entry = self.model.get_value(iter, 1)
                entry.msgstr = self.model.get_value(iter, 4).decode('utf-8')
                self.model.get_value(iter, 0).mofile.save()
                self.model.set_value(iter, 5, False)
            iter = self.model.iter_next(iter)
        self.update_buttons()

    def revert_changes(self):
        iter = self.model.get_iter_first()
        while iter != None:
            if self.model.get_value(iter, 5):
                entry = self.model.get_value(iter, 1)
                self.model.set_value(iter, 4, entry.msgstr) 
                self.model.set_value(iter, 5, False)
            iter = self.model.iter_next(iter)
        self.update_buttons()

    def clear(self):
        self._count = 0
        self.progress.set_text(str(self._count))
        self._loading_queue_lock.acquire()
        self._loading_queue = []
        self._loading_queue_lock.release()
        
        self._loading_lock.acquire()
        is_loading = self._loading
        self._loading_lock.release()
        while is_loading:
            time.sleep(0.1)
            self._loading_lock.acquire()
            is_loading = self._loading
            self._loading_lock.release()
        self.model = Gtk.TreeStore(object, object, str, str, str, bool, GdkPixbuf.Pixbuf, int)
        self.set_model(self.model)

    def _check_loading_progress(self):
        self._loading_lock.acquire()
        self._loaded_data_lock.acquire()
        res = self._loading
        to_load = []
        while len(self._loaded_data) > 0:
            to_load.append(self._loaded_data[0])
            self._loaded_data = self._loaded_data[1:]
        self._loading_lock.release()
        self._loaded_data_lock.release()

        for i in to_load:
            iter = self.model.insert_before(None, None)
            self.model.set_value(iter, 0, i[0])
            self.model.set_value(iter, 1, i[1])
            if self.type == PO_EXT:
                self.model.set_value(iter, 2, "<span color='#0000FF'>%s</span>" % (i[2]))
            else:
                self.model.set_value(iter, 2, i[2])
            self.model.set_value(iter, 3, i[3])
            self.model.set_value(iter, 4, i[4])
            self.model.set_value(iter, 5, False) # dirty flag
            self.model.set_value(iter, 7, i[5])
            self._count += 1
            self.progress.set_text(str(self._count))
        return res

    def load_files(self):
        self.clear()
        for root, subFolders, files in os.walk(os.getcwd(),topdown=False):            
            for file in files:                
                if self.type == MO_EXT:
                    if file.endswith(MO_EXT):
                        path, junk = os.path.split(root)
                        path, locale = os.path.split(path)                        
                        mo_inst = polib.mofile(os.path.join(root, file))
                        mo = Mo(mo_inst, locale, os.path.join(root, file))
                        self.check_file(mo)
                else:
                    if file.endswith(PO_EXT):
                        locale = file.split("-")[-1].replace(".po", "")
                        if locale in ["yi"]:
                            # Don't check PO files for some of the locales (right-to-left languages for instance, or languages where it's hard for us to verify the arguments)
                            continue
                        mo_inst = polib.pofile(os.path.join(root, file))
                        mo = Mo(mo_inst, file, os.path.join(root, file))
                        self.check_file(mo)
        self.progress.set_fraction(1.0)

    def check_file(self, mofile):
        self._loading_queue_lock.acquire()
        self._loading_queue.append(mofile)
        self._loading_queue_lock.release()
        
        start_loading = False
        self._loading_lock.acquire()
        if not self._loading:
            self._loading = True
            start_loading = True
        self._loading_lock.release()
        
        if start_loading:
            self.progress.pulse()
            GObject.timeout_add(100, self._check_loading_progress)
            thread.start_new_thread(self._do_load, ())

    def _do_load(self):
        finished = False
        while not finished:
            self._loading_queue_lock.acquire()
            if len(self._loading_queue) == 0:
                finished = True
            else:
                to_load = self._loading_queue[0]
                self._loading_queue = self._loading_queue[1:]
            self._loading_queue_lock.release()
            if not finished:
                for entry in to_load.mofile:
                    if entry.obsolete:
                        continue # skip obsolete translations (prefixed with #~ in po file)
                    res = self.check_entry(entry)
                    exclude_dates = self.datecheck.get_active()
                    if (res > GOOD and res < BAD_MISCOUNT_MAYBE_DATE) or \
                       (res > BAD_EXCLUSIONS and not exclude_dates):
                        self._loaded_data_lock.acquire()
                        self._loaded_data.append((to_load, entry, to_load.locale, entry.msgid, entry.msgstr, to_load.current_index))
                        self._loaded_data_lock.release()
                    to_load.current_index += 1

        self._loading_lock.acquire()
        self._loading = False
        self._loading_lock.release()

    def check_entry(self, entry, updated_val = None):
        id_tokens = TokenList()
        str_tokens = TokenList()
        msgid = entry.msgid
        if updated_val:
            msgstr = updated_val
        else:
            msgstr = entry.msgstr
        id_date_count = 0
        str_date_count = 0

        for idx in range(len(msgid)):
            try:         
                if msgid[idx] == "%":
                    if msgid[idx-1] > -1 and msgid[idx-1] != "\\":                                                
                        subidx = 0
                        if msgid[idx+1] == "(":
                            while msgid[idx+1+subidx] != ")":
                                subidx += 1
                            token = msgid[idx:(idx+subidx+3)]    
                            id_tokens.add(token)
                        else:
                            subidx = 0
                            catch = ""
                            while True:
                                subidx += 1
                                try:
                                    catch = msgid[idx+subidx]
                                    if allowed(catch):
                                        if catch in COMMON_DATE_TOKENS:
                                            id_date_count += 1
                                        token = msgid[idx:(idx+subidx+1)]
                                        id_tokens.add(token)
                                        break
                                except IndexError:
                                    break
            except:
                pass

        for idx in range(len(msgstr)):
            try:   
                if msgstr[idx] == "%":
                    if msgstr[idx-1] > -1 and msgstr[idx-1] != "\\":
                        subidx = 0
                        if msgstr[idx+1] == "(":
                            while msgstr[idx+1+subidx] != ")":
                                subidx += 1
                            token = msgstr[idx:(idx+subidx+3)]
                            str_tokens.add(token)
                        else:
                            catch = ""
                            subidx = 0
                            while True:
                                subidx += 1
                                try:
                                    catch = msgstr[idx+subidx]
                                    if allowed(catch):
                                        if catch in COMMON_DATE_TOKENS:
                                            str_date_count += 1
                                        token = msgstr[idx:idx+subidx+1]
                                        str_tokens.add(token)
                                        break
                                except IndexError:
                                    break
            except:
                pass
        if msgstr != "":
            if (len(id_tokens) != len(str_tokens)):
                if id_date_count >= DATE_THRESHOLD or str_date_count >= DATE_THRESHOLD:
                    return BAD_MISCOUNT_MAYBE_DATE
                else:
                    return BAD_MISCOUNT
            else:
                mismatch = False
                for j in range(len(id_tokens)):
                    id_token = id_tokens[j]
                    str_token = str_tokens[j]
                    if id_token != str_token:
                        if same_type(id_token, str_token):
                            print "Same type tokens: %s %s" % (id_token, str_token)
                        elif "(" in id_token:
                            #named token, just make sure it corresponds to one of the str_tokens
                            found_token = False
                            for token in str_tokens:
                                if token == id_token:
                                    found_token = True
                                    break
                            if not found_token:
                                print "Couldn't find token: %s" % id_token
                                mismatch = True
                        else:
                            mismatch = True

                if (id_date_count >= DATE_THRESHOLD or str_date_count >= DATE_THRESHOLD) and mismatch:
                    return BAD_MISMATCH_MAYBE_DATE
                elif mismatch:       
                    print id_tokens
                    print str_tokens
                    print ""         
                    return BAD_MISMATCH
        return GOOD

class Main:
    def __init__(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "-po":
                t = PO_EXT
                self.start(t)
            elif sys.argv[1] == "-mo":
                t = MO_EXT
                self.start(t)
            else:
                self.end()
        else:
            self.end()

    def end(self):
        print ""
        print "mocheck: a .po and .mo translation file checker and tweak tool."
        print ""
        print "mocheck searches for errors in format tokens, such as incorrect"
        print "number, non-matching, or out of order conditions.  mocheck will"
        print "then allow you to fix the offending translations by adding order"
        print "codes (%1$d, %2$s, etc..) or missing tokens."
        print ""
        print "Usage:"
        print "       mocheck -po : scan recursively from current directory for .po files"
        print "       mocheck -mo : scan recursively from current directory for .mo files"
        print " "
        quit()

    def start(self, t):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("mocheck.glade")
        self.treebox = self.builder.get_object("treebox")
        self.window = self.builder.get_object("window")
        self.status = self.builder.get_object("status")
        self.refresh_button = self.builder.get_object("refresh")
        self.progress = self.builder.get_object("progress")
        self.datecheck = self.builder.get_object("datecheck")
        self.save = self.builder.get_object("save")
        self.revert = self.builder.get_object("revert")

        self.window.connect("destroy", Gtk.main_quit)
        self.datecheck.connect("toggled", self.on_refresh_clicked)
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.save.connect("clicked", self.on_save_clicked)
        self.revert.connect("clicked", self.on_revert_clicked)

        self.treeview = ThreadedTreeView(self, t)
        self.treebox.add(self.treeview)
        self.treeview.get_selection().connect("changed", lambda x: self.selection_changed());
        self.treeview.connect('button_press_event', self.on_button_press_event)
        self.window.show_all()

        thread.start_new_thread(self.treeview.load_files, ())

    def selection_changed(self):
        model, treeiter = self.treeview.get_selection().get_selected()
        if treeiter:
            entry = self.treeview.model.get_value(treeiter, 1)
            status = self.treeview.check_entry(entry)
            if status == BAD_MISCOUNT:
                self.status.set_text("Number of tokens does not match")
            elif status == BAD_MISCOUNT_MAYBE_DATE:
                self.status.set_text("Number of tokens does not match (could be a date/time)")
            elif status == BAD_MISMATCH:
                self.status.set_text("Tokens not in correct order or mismatch")
            elif status == BAD_MISMATCH_MAYBE_DATE:
                self.status.set_text("Tokens not in correct order or mismatch (could be a date/time)")
            elif status == BAD_UNESCAPED_QUOTE:
                self.status.set_text("Bad quotes")
            else:
                self.status.set_text("")

    def on_button_press_event(self, widget, event):
        if event.button == 1 and self.treeview.type == PO_EXT:
            data=widget.get_path_at_pos(int(event.x),int(event.y))
            if data:
                path, column, x, y = data
                if column.get_property('title')=="Language":
                    iter = self.treeview.model.get_iter(path)
                    pofile = self.treeview.model.get_value(iter, 0)
                    entry = self.treeview.model.get_value(iter, 1)
                    number = self.treeview.model.get_value(iter, 7)
                    locale = pofile.locale
                    self.go_to_launchpad(pofile, locale, number)
                    return False

    def on_refresh_clicked(self, button):
        if self.treeview.dirty:
            if not self.ask("There are unsaved changes - discard them?"):
                return
        thread.start_new_thread(self.treeview.load_files, ())

    def on_save_clicked(self, button):
        self.treeview.save_changes()

    def on_revert_clicked(self, button):
        if self.treeview.dirty:
            if self.ask("There are unsaved changes - discard them?"):
                self.treeview.revert_changes()

    def ask(self, msg):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO,
                                   None)
        dialog.set_default_size(400, 200)
        dialog.set_markup(msg)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def go_to_launchpad(self, pofile, locale, number):
        locale = locale.replace(".po", "")
        domain = "-".join(locale.split("-")[0:-1])
        locale = locale.split("-")[-1]        
        os.system("xdg-open 'https://translations.launchpad.net/linuxmint/latest/+pots/%s/%s/%s/+translate'" % (domain, locale, number))

if __name__ == "__main__":
    Main()
    Gtk.main()
