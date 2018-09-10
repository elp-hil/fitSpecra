
from Tkinter import *
root = Tk()
sv = StringVar()

def validate(var):
    new_value = var.get()
    try:
        new_value == '' or float(new_value)
        validate.old_value = new_value
    except:
        var.set(validate.old_value)    
        validate.old_value = ''

# trace wants a callback with nearly useless parameters, fixing with lambda.
sv.trace('w', lambda nm, idx, mode, var=sv: validate(var))
ent = Entry(root, textvariable=sv)
ent.pack()

root.mainloop()
