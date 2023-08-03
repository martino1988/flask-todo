import datetime
import os
from flask import Flask, render_template, flash, redirect, url_for, request
import csv
import models.models as model
import models.messages_ger as messages
import secrets
import ast


PATH = os.path.dirname(__file__)

class ConfigClass(object):
    SECRET_KEY = secrets.token_hex(16)


app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')


filename_for_lists = messages.FILENAME_FOR_LISTS
filename_for_items = messages.FILENAME_FOR_ITEMS
list_limit = messages.LIST_LIMIT
item_limit = messages.ITEM_LIMIT

def check_for_files():
    if (os.path.exists(filename_for_lists) == False):
        f = open(filename_for_lists, "w")
        print("File for Lists created")
    else:
        print("Filecheck Lists")
    if (os.path.exists(filename_for_items) == False):
        f = open(filename_for_items, "w")
        print("File for Items created")
    else:
        print("Filecheck Items")

check_for_files()


class List:
    def __init__(self, _id, _title):
        self.id = _id
        self.title = _title

def get_new_List_Id():
    ids = []
    with open(filename_for_lists, 'r', newline="") as file:
        for line in file:
            res = ast.literal_eval(line)
            ids.append(res[0])
            
    for i in range(1,list_limit+1):
        if i in ids:
            continue
        else:
            return i

def get_all_lists():
    with open(filename_for_lists, 'r', newline="") as file:
        lists = []
        for line in file:
            res = ast.literal_eval(line)
            list = []
            list.append(res[0])
            list.append(res[1])
            lists.append(list)
        return lists

def get_listname_of_list(id):
    all_lists = get_all_lists()
    for list in all_lists:
        if id == list[0]:
            return list[1]

def change_listname(id, new_name):
    all_lists = get_all_lists()
    for list in all_lists:
        if id == list[0]:
            list[1] = new_name
    with open(filename_for_lists, 'w+', newline="") as file:
        for list in all_lists:
            file.write(str(list))
            file.write("\n")
    


class Item:
    def __init__(self, _id: int, _list_id: int, _title: str, _content: str, _checked: bool):
        self.id = _id
        self.list_id = _list_id
        self.titel = _title
        self.content = _content
        self.checked = _checked

    def change_check(self):
        if self.checked == True:
            self.checked = False
        else:
            self.checked = True


def get_list_items(list_id):
    with open(filename_for_items, 'r', newline="") as file:
        items = []
        for line in file:
            line = ast.literal_eval(line)
            if line[1] == list_id:
                this_Item = Item(
                    _id = line[0],
                    _list_id = line[1],
                    _title = line[2],
                    _content = line[3],
                    _checked = line[4]
                )
                items.append(this_Item)
            else:
                continue
        return items

def get_new_Item_Id():
    ids = []
    with open(filename_for_items, 'r', newline="") as file:
        for line in file:
            res = ast.literal_eval(line)
            ids.append(res[0])
            
    for i in range(1,item_limit+1):
        if i in ids:
            continue
        else:
            return i

def get_item_object(item_id):
    with open(filename_for_items, 'r', newline="") as file:
        for line in file:
            line = ast.literal_eval(line)
            if line[0] == item_id:
                this_Item = Item(
                    _id = line[0],
                    _list_id = line[1],
                    _title = line[2],
                    _content = line[3],
                    _checked = line[4]
                )
                return this_Item
            else:
                continue
    return False
 
def upadate_item(Item):
    items = []
    with open(filename_for_items, 'r', newline="") as file:
        items = [line for line in file]
    print("items ",items)    
    
    items = [ast.literal_eval(line) for line in items]
        
    for line in items:
        if line[0] == Item.id:
            line[2] = Item.titel
            line[3] = Item.content
            line[4] = Item.checked
    
    print("new items ",items) 
    
    with open(filename_for_items, 'w+', newline="") as file:
        for line in items:
            file.write(str(line))
            file.write("\n")



#################### SETTINGS ######################
@app.route("/settings", methods=['GET', 'POST'])
def show_settings():
    settings = []
    settings.append([messages.LABEL_FOR_LISTLIMIT, messages.LIST_LIMIT])
    settings.append([messages.LABEL_FOR_ITEMLIMIT, messages.ITEM_LIMIT])

    return render_template("settings.html", settings=settings)
    
    
    
#################################################################################
################################   DASHBOARD   ##################################
#################################################################################
@app.route('/', methods=['GET', 'POST'])
@app.route("/dashboard", methods=['GET', 'POST'])
def show_dashboard():
    alle_listen = get_all_lists()
    form = model.ShoppingListForm()
    form.listname.label.text = messages.LABEL_FOR_LISTNAME
    form.submit.label.text = messages.BUTTON_SAVE_LABELTEXT
    if form.validate_on_submit():
        new_list = List(
            _id = get_new_List_Id(),
            _title = form.listname.data
        )
        if not new_list.id:
            flash(messages.LIST_LIMIT_REACHED + " Limit:" + str(messages.LIST_LIMIT))
            return redirect(url_for('show_dashboard'))
        try:
            with open(filename_for_lists, 'a', newline="\n") as file:
                list_to_append = []
                list_to_append.append(new_list.id)
                list_to_append.append(new_list.title)
                file.write(str(list_to_append))
                file.write("\n")

            return redirect(url_for('show_dashboard'))
                
        except:
            flash(messages.NEW_LIST_ADD_FAILED)
            return redirect(url_for('show_dashboard'))

    return render_template("dashboard.html", form=form, alle_listen=alle_listen)


####################################   LISTE LÖSCHEN   #############################################
@app.route('/dashboard/liste/delete/<int:id>', methods=['GET', 'POST'])
def show_delete_list(id):
    try:
        with open(filename_for_lists, 'r+', newline="") as file:
            d = file.readlines()
            file.seek(0)
            for line in d:
                if ast.literal_eval(line)[0] != id:
                    file.write(line)
            file.truncate()
        
        with open(filename_for_items, 'r+', newline="") as file:
            d = file.readlines()
            file.seek(0)
            for line in d:
                if ast.literal_eval(line)[1] != id:
                    file.write(line)
            file.truncate()    
            
            
        return redirect(url_for('show_dashboard'))
        
    except:
        flash(messages.LIST_DELETE_FAILED)
        return redirect(url_for('show_dashboard'))
        

####################################   LISTE ÄNDERN   #############################################
@app.route('/dashboard/liste/change/<int:id>', methods=['GET', 'POST'])
def show_change_list(id):
    list_to_change = id
    form = model.ShoppingListForm()
    form.listname.data = get_listname_of_list(id)
    old_name = get_listname_of_list(id)
    if form.validate_on_submit():
        new_listname = request.form.get('listname')
        change_listname(list_to_change, new_listname)
        return redirect(url_for('show_dashboard'))

    return render_template('list.html', form=form)


####################################   LISTE ANZEIGEN   #############################################
@app.route('/dashboard/liste/<int:id>', methods=['GET', 'POST'])
def show_shoppinglist(id):
    this_list_id = id
    all_items = get_list_items(id)
    listname = get_listname_of_list(this_list_id)
    form = model.ItemForm()
    form.itemname.label.text = messages.ITEM_NAME
    form.itemcontent.label.text = messages.ITEM_CONENT
    form.submit.label.text = messages.BUTTON_ADD_LABEL
   
    if form.validate_on_submit():
        new_item = Item(
            _id = get_new_Item_Id(),
            _list_id = this_list_id,
            _title = form.itemname.data,
            _content = form.itemcontent.data,
            _checked = False
        )
        try:
            with open(filename_for_items, 'a', newline="\n") as file:
                list_to_append = []
                list_to_append.append(new_item.id)
                list_to_append.append(new_item.list_id)
                list_to_append.append(new_item.titel)
                list_to_append.append(new_item.content)
                list_to_append.append(new_item.checked)
                file.write(str(list_to_append))
                file.write("\n")
                
            return redirect(url_for('show_shoppinglist', id=this_list_id))
        except:
            flash(messages.NEW_LIST_ITEM_ADD_FAILED)
            return redirect(url_for('show_shoppinglis', id=this_list_id))
            
    return render_template('item_list.html', form=form, Listname=listname, items=all_items)

####################################   ELEMENT EINER LISTE DURCHSTREICHEN   #############################################
@app.route('/dashboard/liste/<int:id>/check_item/<int:item_id>', methods=['GET', 'POST'])
def show_check_item(id, item_id):
    item_to_check = get_item_object(item_id)
    
    try:
        item_to_check.change_check()
        upadate_item(item_to_check)
        return redirect(url_for('show_shoppinglist', id=id))
    except:
        flash(messages.ITEM_UPDATE_FAILED)
        return redirect(url_for('show_shoppinglist', id=id))
		
		
####################################   ELEMENT EINER LISTE LÖSCHEN   #############################################
@app.route('/dashboard/liste/<int:id>/delete_item/<int:item_id>', methods=['GET', 'POST'])
def show_delete_item(id, item_id):
    try:
        with open(filename_for_items, 'r+', newline="") as file:
            d = file.readlines()
            file.seek(0)
            for line in d:
                if ast.literal_eval(line)[0] != item_id:
                    file.write(line)
            file.truncate()
            return redirect(url_for('show_shoppinglist', id=id))
        
    except:
        flash(messages.ITEM_DELETE_FAILED)
        return redirect(url_for('show_shoppinglist', id=id))


####################################   ELEMENT EINER LISTE ÄNDERN   #############################################
@app.route('/dashboard/liste/<int:id>/change_item/<int:item_id>', methods=['GET', 'POST'])
def show_change_item(id, item_id):
    item_to_change = get_item_object(item_id)
    form = model.ItemForm()
    
    form.itemname.label.text = messages.ITEM_NAME
    form.itemcontent.label.text = messages.ITEM_CONENT
    form.submit.label.text = messages.BUTTON_SAVE_LABELTEXT
    
    form.itemname.data = item_to_change.titel
    form.itemcontent.data = item_to_change.content
    
    if form.validate_on_submit():
        item_to_change.titel = request.form.get('itemname')
        item_to_change.content = request.form.get('itemcontent')
        upadate_item(item_to_change)
        return redirect(url_for('show_shoppinglist', id=id))
    return render_template('item.html', form=form)

#################################################################################
#################################################################################



if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
