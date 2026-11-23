"""Tkinter desktop interface for the Beam Designer."""
import tkinter as tk
from tkinter import ttk, messagebox
import math
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
        self.support = tk.StringVar(value="Simply supported")
        self.span = tk.StringVar(value="20")
        self.section = tk.StringVar(value="W12x26")
        self.direction = tk.StringVar(value="Downward")
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
        ttk.Label(left, text="Point loads  (kip @ ft)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,3))
        self.point_frame=ttk.Frame(left); self.point_frame.pack(fill="x")
        ttk.Button(left,text="+ Add point load",command=self.add_point).pack(fill="x",pady=3)
        ttk.Label(left, text="Uniform loads  (kip/ft, start, end)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,3))
        self.uniform_frame=ttk.Frame(left); self.uniform_frame.pack(fill="x")
        ttk.Button(left,text="+ Add uniform load",command=self.add_uniform).pack(fill="x",pady=3)
        self.error=ttk.Label(left, text="", foreground="#b04b4b", wraplength=260); self.error.pack(anchor="w",pady=5)
        self.summary=ttk.Label(right,text="",justify="left",font=("Segoe UI",10),padding=10); self.summary.grid(row=0,column=0,sticky="ew")
        self.fig=Figure(figsize=(8,6),dpi=90); self.axes=self.fig.subplots(4,1,sharex=True); self.fig.tight_layout(pad=2)
        self.canvas=FigureCanvasTkAgg(self.fig,master=right); self.canvas.get_tk_widget().grid(row=1,column=0,sticky="nsew")
        self.span.trace_add("write",lambda *_: self.refresh())
        self.section.trace_add("write",lambda *_: self.refresh()); self.direction.trace_add("write",lambda *_: self.refresh())

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

    def refresh(self):
        if not hasattr(self,"axes"): return
        try:
            span=float(self.span.get())
            if not math.isfinite(span) or not 1<=span<=100: raise ValueError("Span must be between 1 and 100 ft.")
            points=[(float(m.get()),float(x.get())) for m,x in self.point_rows]
            uniforms=[(float(w.get()),float(a.get()),float(b.get())) for w,a,b in self.uniform_rows]
            if any(not all(map(math.isfinite,(m,x))) or not 0<=m<=100 or not 0<=x<=span for m,x in points): raise ValueError("Point loads must be 0–100 kip and within the span.")
            if any(not all(map(math.isfinite,(w,a,b))) or not 0<=w<=10 or a<0 or b>span or a>=b for w,a,b in uniforms): raise ValueError("Uniform loads must be 0–10 kip/ft with start < end inside the span.")
            result=analyze(span,self.support.get(),points,uniforms,self.section.get(),self.direction.get())
        except (ValueError,TypeError) as exc:
            self.error.configure(text=str(exc) or "Enter valid numeric values."); return
        self.error.configure(text="")
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
        for w,a,b in uniforms:
            xs=np.linspace(a,b,8); ax.vlines(xs,.12,.35,color="#75a82f"); ax.text((a+b)/2,.4,f"{w:g} kip/ft",ha="center",fontsize=8)
        ax.set_ylim(-.2,.7); ax.set_yticks([])
        for a in self.axes: a.set_xlim(0,span)
        self.axes[-1].set_xlabel("Position from left end (ft)")
        self.fig.tight_layout(pad=1.4); self.canvas.draw_idle()


if __name__ == "__main__":
    app=BeamApp(); app.redraw_rows(); app.mainloop()
