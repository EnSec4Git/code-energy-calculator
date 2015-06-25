from __future__ import print_function
import __future__
try:
    from Tkinter import Button, Tk, Toplevel, Label, Listbox, Scrollbar,\
        LabelFrame, Entry, Frame, Radiobutton, Text, Checkbutton
    import Tkinter
    import tkMessageBox
    from tkFileDialog import *
except ImportError:
    from tkinter import Button, Tk, Toplevel, Label, Listbox, Scrollbar,\
        LabelFrame, Entry, Frame, Radiobutton, Text, Checkbutton
    import tkinter as Tkinter
    import tkinter.messagebox as tkMessageBox
    from tkinter.filedialog import *
import threading
import math
import os

DEFAULT_CODE = """# Use Python syntax to define the function f that takes
# one argument (the scalar product) and returns the associated energy.
# Example - Riesz energy
def f(x):
    return pow((2*(1-x)),-2)

"""

class MainWindow:
    def __init__(self):
        self.root = Tk()
        self.input_type = Tkinter.IntVar()
        self.input_type.set(1)
        self.normalize_data = Tkinter.IntVar()
        self.normalize_data.set(1)
        self.root.title("Code energy calculator")
        self.left_frame = LabelFrame(self.root,
                                     text="Input and output")
        self.left_frame.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH,
                             expand=True, padx=(10, 5), pady=10)
        self.right_frame = LabelFrame(self.root, text="Code")
        self.right_frame.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH,
                              expand=True, padx=(5, 10), pady=10)
        code_hscroll = Scrollbar(self.right_frame, orient=Tkinter.HORIZONTAL)
        code_hscroll.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        code_vscroll = Scrollbar(self.right_frame)
        code_vscroll.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.code_text = Text(self.right_frame, wrap=Tkinter.NONE,
                              xscrollcommand=code_hscroll.set,
                              yscrollcommand=code_vscroll.set)
        self.code_text.pack()
        self.code_text.insert(Tkinter.INSERT, DEFAULT_CODE)
        code_hscroll.config(command=self.code_text.xview)
        code_vscroll.config(command=self.code_text.yview)
        self.input_file_entry =\
            self.create_and_add_file_field(self.left_frame, "Input file", 5, False)
        self.spherical_coord_option =\
            Radiobutton(self.left_frame, text="Spherical coordinates",
                        variable=self.input_type, value=1)
        self.spherical_coord_option.pack(anchor=Tkinter.W)
        self.cartesian_coord_option =\
            Radiobutton(self.left_frame, text="Cartesian coordinates",
                        variable=self.input_type, value=2)
        self.cartesian_coord_option.pack(anchor=Tkinter.W)
        self.spherical_coord_option.select()
        self.output_file_entry =\
            self.create_and_add_file_field(self.left_frame, "Output file", 5, True)
        self.normalize_check = Checkbutton(self.left_frame, text="Normalize data",
                                           variable=self.normalize_data,
                                           offvalue=0, onvalue=1)
        self.normalize_check.pack()
        self.normalize_check.deselect()
        self.do_button = Button(self.left_frame, text="Run", command=self.run)
        self.do_button.pack(side=Tkinter.BOTTOM, pady=(0, 10))

    def create_and_add_file_field(self, parent, title, pad, is_save):
        title_label = Label(parent, text=title)
        title_label.pack(side=Tkinter.TOP, padx=pad)
        container_frame = Frame(parent)
        container_frame.pack(side=Tkinter.TOP, padx=pad, pady=(0, pad))
        filename_entry = Entry(container_frame)
        filename_entry.pack(side=Tkinter.LEFT)
        browse_button = \
            Button(container_frame, text="Browse...",
                   command=lambda: self.select_file(filename_entry, is_save))
        browse_button.pack(side=Tkinter.RIGHT)
        return filename_entry

    @staticmethod
    def select_file(text_field, is_save):
        text_field.delete(0, Tkinter.END)
        if is_save:
            filename = asksaveasfilename()
        else:
            filename = askopenfilename()
        text_field.insert(0, filename)

    def run(self):
        input_fname = self.input_file_entry.get()
        output_fname = self.output_file_entry.get()
        code = self.code_text.get(1.0, Tkinter.END)
        do_work(input_fname, output_fname, code,
                self.input_type.get(), self.normalize_data.get())

    def show(self):
        self.root.mainloop()


def spherical_to_cartesian(ro, azim, incl):
    x = ro * math.sin(incl) * math.cos(azim)
    y = ro * math.sin(incl) * math.sin(azim)
    z = ro * math.cos(incl)
    return (x,y,z)

def scalar_product(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

def sqr(x):
    return x*x

def normalized(pt):
    length = math.sqrt(sqr(pt[0]) + sqr(pt[1]) + sqr(pt[2]))
    if length==0:
        return pt
    return (pt[0] / length, pt[1] / length, pt[2] / length)

def do_work(input_fname, output_fname, code, input_type, should_normalize):

    # Parse input
    fin = open(input_fname, 'r')
    if not fin:
        tkMessageBox.showerror("Error", "Cannot open input file")
    fout = open(output_fname, 'w')
    if not fout:
        tkMessageBox.showerror("Error", "Cannot open output file")
    points = []
    for line in fin:
        parts = line.split()
        if(len(parts) < 3):
            break
        point = None
        if input_type == 2:
            point = (float(parts[0]), float(ports[1]), float(ports[2]))
        elif input_type == 1:
            point =\
                spherical_to_cartesian(float(parts[0]), float(parts[1]),
                                       float(parts[2]))
        else:
            print(input_type)
            raise RuntimeError("Don't know how to handle this input type")
        points.append(point)

    # Run the code the user wrote
    user_namespace = {}
    exec(code, user_namespace)
    f = user_namespace["f"]
    print(f)

    # Normalize points if necessary
    if should_normalize:
        for i in range(len(points)):
            points[i] = normalized(points[i])

    # Calculate code energy
    energy_sum = 0
    for i in range(len(points)):
        print(points[i])
        for j in range(i+1, len(points)):
            pt1 = points[i]
            pt2 = points[j]
            sp = scalar_product(pt1, pt2)
            energy_sum += f(sp)

    # Output
    print(energy_sum, file=fout)

    # Notify user
    tkMessageBox.showinfo("Done!", "Calculation complete. The answer is: " + str(energy_sum))

def main():
    main_window = MainWindow()
    main_window.show()

if __name__=="__main__":
    main()
