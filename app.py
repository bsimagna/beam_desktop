"""Tkinter desktop interface for the Beam Designer."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import json
import csv
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from beam_calculations import SECTIONS, analyze


class BeamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beam Designer")
        self.geometry("1280x850")
        self.minsize(980, 680)
        self.configure(bg="#f4f7ef")
        menubar=tk.Menu(self)
        file_menu=tk.Menu(menubar,tearoff=False)
        file_menu.add_command(label="Save",command=self.save_design,accelerator="Ctrl+S")
        file_menu.add_command(label="Open",command=self.open_design,accelerator="Ctrl+O")
        menubar.add_cascade(label="File",menu=file_menu)
        self.configure(menu=menubar)
        self.bind_all("<Control-s>",lambda event:self.save_design())
        self.bind_all("<Control-o>",lambda event:self.open_design())
        self.support = tk.StringVar(value="Simply supported")
        self.span = tk.StringVar(value="20")
        self.section = tk.StringVar(value="W12x26")
        self.direction = tk.StringVar(value="Downward")
        self.deflection_limit = tk.StringVar(value="0.6666666667")
        self.point_rows = [(tk.StringVar(value="2"), tk.StringVar(value="10"))]
        self.uniform_rows = [(tk.StringVar(value="1"), tk.StringVar(value="0"), tk.StringVar(value="20"))]
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="BEAM DESIGNER", font=("Segoe UI", 18, "bold"), background="#3f5a2a", foreground="white", padding=14).pack(fill="x")
        body = ttk.Frame(self, padding=12); body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)
        left = ttk.Frame(body, padding=12); left.grid(row=0, column=0, sticky="nsw")
        right = ttk.Frame(body); right.grid(row=0, column=1, sticky="nsew", padx=(12,0)); right.columnconfigure(0, weight=1); right.rowconfigure(1, weight=1)
        ttk.Label(left, text="Beam inputs", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,8))
        ttk.Label(left, text="Support").pack(anchor="w")
        for item in ("Simply supported", "Cantilever"):
            ttk.Radiobutton(left, text=item, variable=self.support, value=item, command=self.refresh).pack(anchor="w")
        self._field(left, "Span (ft)", self.span)
        self._field(left, "Section", self.section, values=list(SECTIONS))
        self._field(left, "Load direction", self.direction, values=["Downward", "Upward"])
        self._field(left, "Deflection limit (in)", self.deflection_limit)
        ttk.Label(left, text="Point loads  (kip @ ft)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,3))
        self.point_frame=ttk.Frame(left); self.point_frame.pack(fill="x")
        ttk.Button(left,text="+ Add point load",command=self.add_point).pack(fill="x",pady=3)
        ttk.Label(left, text="Uniform loads  (kip/ft, start, end)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,3))
        self.uniform_frame=ttk.Frame(left); self.uniform_frame.pack(fill="x")
        ttk.Button(left,text="+ Add uniform load",command=self.add_uniform).pack(fill="x",pady=3)
        ttk.Button(left,text="Export results to CSV",command=self.export_results).pack(fill="x",pady=(8,3))
        ttk.Button(left,text="Export calculation sheet (PDF)",command=self.export_calculation_sheet).pack(fill="x",pady=3)
        self.error=ttk.Label(left, text="", foreground="#b04b4b", wraplength=260); self.error.pack(anchor="w",pady=5)
        self.summary=ttk.Label(right,text="",justify="left",font=("Segoe UI",10),padding=10); self.summary.grid(row=0,column=0,sticky="ew")
        self.fig=Figure(figsize=(8,6),dpi=90); self.axes=self.fig.subplots(4,1,sharex=True); self.fig.tight_layout(pad=2)
        self.canvas=FigureCanvasTkAgg(self.fig,master=right); self.canvas.get_tk_widget().grid(row=1,column=0,sticky="nsew")
        self.span.trace_add("write",lambda *_: self.refresh())
        self.section.trace_add("write",lambda *_: self.refresh()); self.direction.trace_add("write",lambda *_: self.refresh())
        self.deflection_limit.trace_add("write",lambda *_: self.refresh())

    def _field(self,parent,label,var,values=None):
        ttk.Label(parent,text=label).pack(anchor="w",pady=(5,1))
        widget=ttk.Combobox(parent,textvariable=var,values=values,state="readonly") if values else ttk.Entry(parent,textvariable=var,width=20)
        widget.pack(fill="x"); widget.bind("<<ComboboxSelected>>",lambda e:self.refresh())

    def _rows(self, frame, rows, kind):
        for child in frame.winfo_children(): child.destroy()
        for i,row in enumerate(rows):
            holder=ttk.Frame(frame); holder.pack(fill="x",pady=2)
            for j,var in enumerate(row):
                e=ttk.Entry(holder,textvariable=var,width=7); e.pack(side="left",padx=1); var.trace_add("write",lambda *_:self.refresh())
            ttk.Button(holder,text="×",width=2,command=lambda n=i,k=kind:self.remove_row(k,n)).pack(side="left")

    def redraw_rows(self):
        self._rows(self.point_frame,self.point_rows,"p"); self._rows(self.uniform_frame,self.uniform_rows,"u")

    def add_point(self): self.point_rows.append((tk.StringVar(value="0"),tk.StringVar(value="10"))); self.redraw_rows(); self.refresh()
    def add_uniform(self): self.uniform_rows.append((tk.StringVar(value="0"),tk.StringVar(value="0"),tk.StringVar(value=self.span.get() or "20"))); self.redraw_rows(); self.refresh()
    def remove_row(self,k,n):
        rows=self.point_rows if k=="p" else self.uniform_rows
        rows.pop(n); self.redraw_rows(); self.refresh()

    def _current_design(self):
        span=float(self.span.get())
        limit=float(self.deflection_limit.get())
        points=[[float(m.get()),float(x.get())] for m,x in self.point_rows]
        uniforms=[[float(w.get()),float(a.get()),float(b.get())] for w,a,b in self.uniform_rows]
        return {"version":1,"support":self.support.get(),"span_ft":span,
                "section":self.section.get(),"deflection_limit_in":limit,
                "direction":self.direction.get(),"point_loads":points,
                "uniform_loads":uniforms}

    @staticmethod
    def _validate_design(data):
        if not isinstance(data,dict) or data.get("version") != 1:
            raise ValueError("Unsupported or invalid Beam Designer file version.")
        if data.get("support") not in ("Simply supported","Cantilever"):
            raise ValueError("Invalid support type in file.")
        if data.get("section") not in SECTIONS:
            raise ValueError("Unknown section in file.")
        if data.get("direction") not in ("Downward","Upward"):
            raise ValueError("Invalid load direction in file.")
        span=data.get("span_ft"); limit=data.get("deflection_limit_in")
        if isinstance(span,bool) or not isinstance(span,(int,float)) or not math.isfinite(span) or not 1<=span<=100:
            raise ValueError("Span in file must be between 1 and 100 ft.")
        if isinstance(limit,bool) or not isinstance(limit,(int,float)) or not math.isfinite(limit) or limit<=0:
            raise ValueError("Deflection limit in file must be a positive number of inches.")
        points=data.get("point_loads"); uniforms=data.get("uniform_loads")
        if not isinstance(points,list) or not isinstance(uniforms,list):
            raise ValueError("Load lists are missing or invalid.")
        for row in points:
            if (not isinstance(row,list) or len(row)!=2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in row)
                    or not 0<=row[0]<=100 or not 0<=row[1]<=span):
                raise ValueError("File contains an invalid point load.")
        for row in uniforms:
            if (not isinstance(row,list) or len(row)!=3 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in row)
                    or not 0<=row[0]<=10 or not 0<=row[1]<row[2]<=span):
                raise ValueError("File contains an invalid uniform load.")

    def save_design(self):
        try:
            data=self._current_design()
            self._validate_design(data)
        except (ValueError,TypeError) as exc:
            messagebox.showerror("Cannot save design",str(exc),parent=self); return
        path=filedialog.asksaveasfilename(parent=self,title="Save beam design",defaultextension=".json",
                filetypes=[("Beam Designer files","*.json"),("All files","*.*")])
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as file:
                json.dump(data,file,indent=2,ensure_ascii=False)
                file.write("\n")
        except OSError as exc:
            messagebox.showerror("Save failed",f"Could not save the design:\n{exc}",parent=self)

    def open_design(self):
        path=filedialog.askopenfilename(parent=self,title="Open beam design",
                filetypes=[("Beam Designer files","*.json"),("All files","*.*")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as file:
                data=json.load(file)
            self._validate_design(data)
        except (OSError,json.JSONDecodeError,ValueError,TypeError) as exc:
            messagebox.showerror("Cannot open design",str(exc),parent=self); return
        # Apply only after the whole document has been parsed and validated.
        self.support.set(data["support"]); self.span.set(str(data["span_ft"]))
        self.section.set(data["section"]); self.direction.set(data["direction"])
        self.deflection_limit.set(str(data["deflection_limit_in"]))
        self.point_rows=[(tk.StringVar(value=str(m)),tk.StringVar(value=str(x))) for m,x in data["point_loads"]]
        self.uniform_rows=[(tk.StringVar(value=str(w)),tk.StringVar(value=str(a)),tk.StringVar(value=str(b))) for w,a,b in data["uniform_loads"]]
        self.redraw_rows(); self.refresh()

    def export_results(self):
        if getattr(self,"last_analysis",None) is None:
            messagebox.showerror("Cannot export results","Enter valid beam inputs before exporting.",parent=self)
            return
        path=filedialog.asksaveasfilename(parent=self,title="Export beam results",defaultextension=".csv",
                filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path: return
        result=self.last_analysis
        try:
            # UTF-8 with BOM and CRLF records improve compatibility with Excel.
            with open(path,"w",encoding="utf-8-sig",newline="") as file:
                writer=csv.writer(file,lineterminator="\r\n")
                writer.writerow(["x (ft)","V (kip)","M (kip-ft)","Deflection (in)"])
                writer.writerows(zip(result["x"],result["shear"],result["moment"],result["deflection"]))
        except OSError as exc:
            messagebox.showerror("Export failed",f"Could not export results:\n{exc}",parent=self)
            return
        messagebox.showinfo("Export complete",f"Beam results exported to:\n{path}",parent=self)

    def export_calculation_sheet(self):
        if getattr(self,"last_analysis",None) is None:
            messagebox.showerror("Cannot export calculation sheet","Enter valid beam inputs before exporting.",parent=self)
            return
        path=filedialog.asksaveasfilename(parent=self,title="Save calculation sheet",defaultextension=".pdf",
                filetypes=[("PDF files","*.pdf"),("All files","*.*")])
        if not path: return
        r=self.last_analysis; sec=r["section"]
        try:
            span=float(self.span.get())
            point_loads=[(float(m.get()),float(x.get())) for m,x in self.point_rows]
            uniform_loads=[(float(w.get()),float(a.get()),float(b.get())) for w,a,b in self.uniform_rows]
            point_text="; ".join(f"{m:g} kip at {x:g} ft" for m,x in point_loads) or "None"
            uniform_text="; ".join(f"{w:g} kip/ft from {a:g} to {b:g} ft" for w,a,b in uniform_loads) or "None"
            reaction=(f"Vertical reaction: {r['RA']:.3f} kip; fixed-end moment: {r['fixed_moment']:.3f} kip-ft"
                      if self.support.get()=="Cantilever" else f"Reactions: R1 = {r['RA']:.3f} kip; R2 = {r['RB']:.3f} kip")
            inputs=(f"Support: {self.support.get()}    Span: {span:g} ft    Section: {sec.name} ({sec.material})\n"
                    f"Load direction: {self.direction.get()}    Deflection limit: {r['deflection_limit']:.4g} in\n"
                    f"Point loads: {point_text}\nUniform loads: {uniform_text}")
            checks=(f"{reaction}\n"
                    f"Bending: {r['stress']:.3f} ksi / {sec.Fb:g} ksi allowable — {'PASS' if r['bending_pass'] else 'FAIL'}    "
                    f"Max deflection: {abs(r['max_deflection']):.4f} in at {r['max_deflection_x']:.3f} ft / "
                    f"{r['deflection_limit']:.4g} in limit — {'PASS' if r['deflection_pass'] else 'FAIL'}")
            report=Figure(figsize=(11.7,8.3),dpi=150)
            report.text(.06,.96,"Beam Designer — Calculation Sheet",fontsize=17,weight="bold",va="top")
            report.text(.06,.91,"INPUTS",fontsize=9,weight="bold",va="top")
            report.text(.06,.885,inputs,fontsize=8.5,va="top",linespacing=1.4)
            report.text(.06,.755,"GOVERNING CHECKS",fontsize=9,weight="bold",va="top")
            report.text(.06,.73,checks,fontsize=8.5,va="top",linespacing=1.4)
            axes=report.subplots(4,1,sharex=True)
            x=r["x"]
            for ax,title,data,color in zip(axes,["Beam and loads","Shear V (kip)","Moment M (kip-ft)","Deflection (in)"],
                    [None,r["shear"],r["moment"],r["deflection"]],["#26351f","#75a82f","#3f7d63","#c48a28"]):
                ax.set_title(title,loc="left",fontsize=8,pad=2); ax.grid(True,alpha=.2)
                if data is not None:
                    ax.plot(x,data,color=color,linewidth=1.2); ax.axhline(0,color="#777",linewidth=.5)
            beam_ax=axes[0]; beam_ax.plot([0,span],[0,0],color="#26351f",linewidth=4)
            for m,px in point_loads:
                beam_ax.annotate(f"{m:g} kip",(px,0),xytext=(px,.23),ha="center",fontsize=6,
                                 arrowprops={"arrowstyle":"->","color":"#75a82f","lw":.8})
            colors=["#75a82f","#377eb8","#e68632","#9b59a6","#d64f5f","#159a94","#8c6d31","#555555"]
            for i,(w,a,b) in enumerate(uniform_loads):
                if w<=0: continue
                color=colors[i%len(colors)]; length=.35*w/10
                rail=(-length if self.direction.get()=="Upward" else length)
                beam_ax.hlines(rail,a,b,color=color,linewidth=.8)
                for px in np.linspace(a,b,max(3,min(14,int((b-a)/span*14)+2))):
                    beam_ax.annotate("",xy=(px,0),xytext=(px,rail),arrowprops={"arrowstyle":"-|>","color":color,"lw":.7,"mutation_scale":6})
            beam_ax.set_ylim(-.55,.55); beam_ax.set_yticks([])
            for ax in axes: ax.set_xlim(0,span)
            axes[-1].set_xlabel("Position from left end (ft)",fontsize=7)
            report.subplots_adjust(left=.08,right=.97,bottom=.07,top=.62,hspace=.52)
            report.savefig(path,format="pdf",bbox_inches="tight")
        except (OSError,ValueError,TypeError) as exc:
            messagebox.showerror("PDF export failed",f"Could not create calculation sheet:\n{exc}",parent=self)
            return
        messagebox.showinfo("Export complete",f"Calculation sheet saved to:\n{path}",parent=self)

    def refresh(self):
        if not hasattr(self,"axes"): return
        try:
            span=float(self.span.get())
            if not math.isfinite(span) or not 1<=span<=100: raise ValueError("Span must be between 1 and 100 ft.")
            limit=float(self.deflection_limit.get())
            if not math.isfinite(limit) or limit<=0: raise ValueError("Deflection limit must be a positive number of inches.")
            points=[(float(m.get()),float(x.get())) for m,x in self.point_rows]
            uniforms=[(float(w.get()),float(a.get()),float(b.get())) for w,a,b in self.uniform_rows]
            if any(not all(map(math.isfinite,(m,x))) or not 0<=m<=100 or not 0<=x<=span for m,x in points): raise ValueError("Point loads must be 0–100 kip and within the span.")
            if any(not all(map(math.isfinite,(w,a,b))) or not 0<=w<=10 or a<0 or b>span or a>=b for w,a,b in uniforms): raise ValueError("Uniform loads must be 0–10 kip/ft with start < end inside the span.")
            result=analyze(span,self.support.get(),points,uniforms,self.section.get(),self.direction.get(),deflection_limit=limit)
        except (ValueError,TypeError) as exc:
            self.last_analysis=None
            self.error.configure(text=str(exc) or "Enter valid numeric values."); return
        self.error.configure(text="")
        self.last_analysis=result
        r=result; sec=r["section"]
        react=f"Reactions: R₁ {r['RA']:.2f} kip"+(f", R₂ {r['RB']:.2f} kip" if self.support.get()=="Simply supported" else f"; fixed moment {r['fixed_moment']:.2f} kip-ft")
        self.summary.configure(text=f"{react}    |    max |V| {abs(r['max_shear']):.2f} kip at {r['max_shear_x']:.2f} ft    |    max |M| {r['max_moment']:.2f} kip-ft at {r['max_moment_x']:.2f} ft\nMax |deflection| {abs(r['max_deflection']):.3f} in at {r['max_deflection_x']:.2f} ft    |    bending {r['stress']:.2f}/{sec.Fb:g} ksi {'PASS' if r['bending_pass'] else 'FAIL'}    |    deflection {r['deflection_limit']:.3f} in limit {'PASS' if r['deflection_pass'] else 'FAIL'}")
        titles=["Beam / loads", "Shear (kip)", "Moment (kip-ft)", "Deflection (in)"]
        series=[None,r["shear"],r["moment"],r["deflection"]]
        for ax,title,data in zip(self.axes,titles,series):
            ax.clear(); ax.set_title(title,loc="left",fontsize=9); ax.grid(True,alpha=.2)
            if data is not None:
                ax.plot(r["x"],data,color="#75a82f" if title.startswith("Shear") else "#3f7d63" if title.startswith("Moment") else "#c48a28")
                ax.axhline(0,color="#777",linewidth=.6)
        ax=self.axes[0]; ax.plot([0,span],[0,0],color="#26351f",linewidth=5)
        for m,x in points:
            ax.annotate(f"{m:g} kip",(x,0),xytext=(x,.25),ha="center",arrowprops={"arrowstyle":"->","color":"#75a82f"},fontsize=8)
        load_colors=["#75a82f", "#377eb8", "#e68632", "#9b59a6", "#d64f5f", "#159a94", "#8c6d31", "#555555"]
        for load_index,(w,a,b) in enumerate(uniforms):
            if w <= 0:
                continue
            upward = self.direction.get() == "Upward"
            color=load_colors[load_index % len(load_colors)]
            xs=np.linspace(a,b,max(3,min(14,int((b-a)/span*14)+2)))
            vector_length = .40 * w / 10.0
            rail_y = -vector_length if upward else vector_length
            tip_y = 0.0
            ax.hlines(rail_y,a,b,color=color,linewidth=1.2)
            for x_arrow in xs:
                ax.annotate("",xy=(x_arrow,tip_y),xytext=(x_arrow,rail_y),
                            arrowprops={"arrowstyle":"-|>","color":color,"lw":1.1,"mutation_scale":8})
            ax.text((a+b)/2,rail_y+(-.035 if upward else .035),f"{w:g} kip/ft",ha="center",fontsize=8,
                    color=color,va="top" if upward else "bottom")
        # Dimension line below the beam, marking every point-load position and
        # both boundaries of each distributed load.
        dim_y=-.58
        positions=sorted({x for _,x in points} | {x for _,a,b in uniforms for x in (a,b)})
        if positions:
            ax.hlines(dim_y,0,span,color="#66745f",linewidth=.8)
            ax.vlines([0,span],dim_y-.025,dim_y+.025,color="#66745f",linewidth=.8)
        for position in positions:
            ax.vlines(position,dim_y-.035,dim_y+.035,color="#66745f",linewidth=.8)
            ax.text(position,dim_y-.055,f"{position:g} ft",ha="center",va="top",fontsize=7,color="#4a5744")
        ax.set_ylim(-.82,.7); ax.set_yticks([])
        for a in self.axes: a.set_xlim(0,span)
        self.axes[-1].set_xlabel("Position from left end (ft)")
        self.fig.tight_layout(pad=1.4); self.canvas.draw_idle()


if __name__ == "__main__":
    app=BeamApp(); app.redraw_rows(); app.mainloop()
