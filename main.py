from Tkinter import *
import tkFileDialog
import clusters
from PIL import Image as PImage
from PIL import ImageTk
from ttk import Combobox
class district():
    def __init__(self, name):
        self.name = name
        self.election_results = {}
class party():
    def __init__(self, acronym):
        self.acronym = acronym
        self.election_results = {}
class data_center():
    def __init__(self):
        self.districts = {}
        self.parties = {}
    def load_data(self):
        filename = tkFileDialog.askopenfilename(initialdir="/", title="Select Election Data",filetypes=(("All Files", "*.*"), ("all files", "*.*")))
        new_file = open(filename, 'r')
        text = new_file.read().strip("\n")
        if "Toplam secmen sayisi" not in text:  # To prevent opening another file
            raise IndexError
        data_list = text.split("Kaynak: YSK")
        data_list.pop(0)
        for i in data_list:
            d_name = i.split("\n")[1]  # District Name
            self.districts[d_name] = district(d_name)  # Create district object
            for j in i.split("\n")[8:]:
                if j.split("\t")[0] == "Toplam" or j.split("\t")[0]=="Gecersiz ya da bos" or j.split("\t")[0] == "Katilim orani" or j.split("\t")[0] == "" or j.split("\t")[0] == "BGMSZ":
                    pass
                else:
                    # j.split("\t")[0] ===> Party
                    # j.split("\t")[4] ===> Vote %
                    if j.split("\t")[0] not in self.parties:  # If party name not in parties dictionary
                        self.parties[j.split("\t")[0]] = party(j.split("\t")[0]) # Create party object
                        self.parties[j.split("\t")[0]].election_results[d_name] = float(j.split("\t")[4].strip("%"))  # Add vote percentage in this district to party object
                    else:
                        self.parties[j.split("\t")[0]].election_results[d_name] = float(j.split("\t")[4].strip("%"))  # Add vote percentage in this district to party object
                    self.districts[d_name].election_results[j.split("\t")[0]] = float(j.split("\t")[4].strip("%"))  # Add vote percantage of this party to the district object
    def cluster(self,d_or_p = 0, selected = [], threshold=0):
        # Create a matrix as shown in lecture slides:
        if d_or_p == 0:  # If clustering districts
            out = file('electiondata.txt', 'w')
            out.write("Party")
            for i in self.parties:
                out.write('\t%s' % i)
            out.write('\n')
            if selected == []:  # If no districts specified, cluster all of them
                selected = self.districts
            for i in selected:
                out.write(i)
                for j in self.parties:
                    if j in self.districts[i].election_results and self.districts[i].election_results[j] >= threshold:  # If it exists and bigger/equal than the threshold
                        out.write('\t%f' % self.districts[i].election_results[j])
                    else:
                        out.write('\t0')
                out.write('\n')
            out.close()
            p, d, data = clusters.readfile('electiondata.txt')
            clust = clusters.hcluster(data, distance=clusters.sim_distance)
            clusters.drawdendrogram(clust, p, jpeg='cluster.jpg')
        else:  # If clustering parties
            out = file('electiondata.txt', 'w')
            out.write("Party")
            if not selected:
                selected = self.districts
            for i in sorted(selected):
                out.write('\t%s' % i)
            out.write('\n')
            for i in sorted(self.parties):
                out.write(i)
                for j in sorted(selected):
                    if j in self.parties[i].election_results and self.parties[i].election_results[j] >= threshold:  # If it exists and bigger/equal than the threshold
                        out.write('\t%f' % self.parties[i].election_results[j])
                    else:
                        out.write('\t0')
                out.write('\n')
            out.close()
            p, d, data = clusters.readfile('electiondata.txt')
            clust = clusters.hcluster(data, distance=clusters.sim_distance)
            clusters.drawdendrogram(clust, p, jpeg = 'cluster.jpg')
class GUI(Frame):
    def __init__(self,parent):
        self.parent = parent
        Frame.__init__(self,parent)
        self.initUI(parent)
        self.data = data_center()
    def initUI(self, parent):
        self.color_bg = "#E0E1E1"
        self.color_headding = "#306998"
        self.color_button = "#4B8BBE"
        self.color_active = "white"
        self.color_disabled = "#FFD43B"
        self.color_lb = "#FFE873"
        self.configure(bg=self.color_bg)
        self.canvas_drawn = False
        self.data_loaded = False
        self.frame_buttons_top = Frame(self,bg=self.color_bg,bd=-2,)
        self.frame_buttons_bottom = Frame(self,bg=self.color_bg,bd=-2)
        self.frame_canvas = Frame(self,bg="white", bd=-2,height=300)
        self.frame_canvas.columnconfigure(0, weight=1)
        self.frame_bottom = Frame(self,bg=self.color_bg)
        self.frame_bottom_list = Frame(self.frame_bottom, bg=self.color_bg)
        self.frame_bottom_combo = Frame(self.frame_bottom, bg=self.color_bg)
        self.label_header = Label(self, width=120, text="ELECTION DATA ANALYSIS TOOL", font=("Century Gothic", 11), bg=self.color_headding, fg="white")
        self.label_header.pack(ipadx=60, ipady=5, pady=(0,20), fill=X)
        self.button_election = Button(self.frame_buttons_top,width=20,height=2, text="Load Election Data",relief="groove",  bg=self.color_button, fg="white", command=self.open_file)
        self.button_election.pack(pady=(0,30))
        self.button_districts = Button(self.frame_buttons_bottom, width=40,height=2,bd=-2, text="Cluster Districts", relief="flat", bg=self.color_disabled, command=self.cluster_districts)
        self.button_districts.pack(side=LEFT, padx=30,pady=0)
        self.button_parties = Button(self.frame_buttons_bottom, width=40,height=2,bd=-2, text="Cluster Political Parties", relief="flat", bg=self.color_disabled, command=self.cluster_parties)
        self.button_parties.pack(side=LEFT, padx=30, pady=0)
        self.frame_buttons_top.pack()
        self.frame_buttons_bottom.pack(pady=0,ipady=0)
        self.frame_canvas.pack(fill=X, expand=True)
        self.frame_bottom.pack(expand=True, pady=20)
        self.pack(fill=X)
    def open_file(self):
        try:
            self.data.load_data()
            self.data_loaded = True
        except Exception:
            self.data_loaded = False
    def draw_image(self):
        self.canvas.yview('moveto',0) # Reset scroller position
        self.canvas.xview('moveto',0)
        self.canvas.delete("image") # Delete the existing image before inserting the new one
        self.pimage = PImage.open("cluster.jpg")
        self.image = ImageTk.PhotoImage(self.pimage)
        width = self.image.width()
        height = self.image.height()
        self.canvas.config(scrollregion=(0,0,width+30,height+30)) # Scroll region is determined by the size of the image
        self.canvas.create_image(20,20,anchor=N+W,image=self.image, tags="image")
    def create_bottom(self):
        self.district_list_label = Label(self.frame_bottom_list, width=50, text="Districts", bg=self.color_headding, fg="white")
        self.district_list_label.grid(row=0, column=0, columnspan=2, sticky=W+E)
        self.district_list = Listbox(self.frame_bottom_list, relief="flat", selectmode=MULTIPLE, selectforeground="black", selectbackground=self.color_lb, exportselection=False)
        self.district_list.grid(row=1, column=0,sticky=W+E)
        self.district_list_scroll = Scrollbar(self.frame_bottom_list, orient=VERTICAL, command=self.district_list.yview)
        self.district_list_scroll.grid(row=1, column=1, sticky=N+S)
        self.district_list.config(yscrollcommand=self.district_list_scroll.set)
        self.frame_bottom_list.pack(side=LEFT,fill=X,expand=True)
        self.frame_bottom_list.columnconfigure(0,weight=1)
        for i in sorted(self.data.districts):
            self.district_list.insert(END, i)
        self.combo_label = Label(self.frame_bottom_combo, text="Threshold", bg=self.color_headding, fg="white")
        self.combo_label.grid(row=0,column=0,sticky=E+W)
        self.combo = Combobox(self.frame_bottom_combo, state="readonly",values=["0%","1%","10%","20%","30%","40%","50%"],width=20)
        self.combo.grid(row=1,column=0)
        self.combo.current(0)
        self.frame_bottom_combo.pack(side=LEFT, fill=BOTH, padx=30)
        self.frame_bottom_combo.rowconfigure(2, weight=1)
        self.button_refine = Button(self.frame_bottom_combo, height=2, text="Refine Analysis", relief="groove",fg="white", bg=self.color_button, command=self.refine)
        self.button_refine.grid(row=2,column=0,sticky=E+W+N, pady=30)
    def draw_canvas(self):
        if not self.canvas_drawn:
            self.canvas = Canvas(self.frame_canvas, bg="white", bd=-2,highlightthickness=-2)
            self.canvas.grid(row=0, column=0,  sticky=W+E)
            self.canvas_drawn = True
            self.c_scroll_y = Scrollbar(self.frame_canvas, orient=VERTICAL, command=self.canvas.yview)
            self.c_scroll_y.grid(row=0, column=1, sticky=N+S)
            self.c_scroll_x = Scrollbar(self.frame_canvas, orient=HORIZONTAL, command=self.canvas.xview)
            self.c_scroll_x.grid(row=1, column=0, sticky=W+E)
            self.canvas.config(yscrollcommand=self.c_scroll_y.set, xscrollcommand=self.c_scroll_x.set)
            self.create_bottom()
    def cluster_districts(self):
        if self.data_loaded:
            self.button_districts.configure(bg=self.color_active)
            self.button_parties.configure(bg=self.color_disabled)
            self.d_or_p = 0
            self.draw_canvas()
            self.threshhold = int(self.combo.get().strip("%"))
            self.selected = []
            selection = self.district_list.curselection()
            for i in selection:
                self.selected.append(self.district_list.get(i))
            self.data.cluster(d_or_p=self.d_or_p, selected=self.selected, threshold=self.threshhold)
            self.draw_image()
    def cluster_parties(self):
        if self.data_loaded:
            self.button_parties.configure(bg=self.color_active)
            self.button_districts.configure(bg=self.color_disabled)
            self.d_or_p = 1
            self.draw_canvas()
            self.threshhold = int(self.combo.get().strip("%"))
            self.selected = []
            selection = self.district_list.curselection()
            for i in selection:
                self.selected.append(self.district_list.get(i))
            self.data.cluster(d_or_p=self.d_or_p, selected=self.selected, threshold=self.threshhold)
            self.draw_image()
    def refine(self):
        if self.d_or_p == 0:
            self.cluster_districts()
        else:
            self.cluster_parties()
        self.district_list.yview(0) # Reset scroll position of the districts listbox
        self.district_list.selection_clear(0, END) # Clear the selection of districts
        self.frame_bottom_combo.focus_set() # Remove the focus on the combobox
def main():
    root = Tk()
    root.title("Election Data Analysis Tool")
    app = GUI(root)
    root.mainloop()
main()