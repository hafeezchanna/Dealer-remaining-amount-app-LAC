import csv,os,re,webbrowser,urllib.parse,tkinter as tk
from tkinter import ttk,filedialog,messagebox
DATA=os.path.join(os.path.dirname(__file__),"dealers.csv")
def phone(p):
 d=re.sub(r"\\D","",p or "")
 return "92"+d[1:] if d.startswith("03") and len(d)==11 else ("92"+d if d.startswith("3") and len(d)==10 else "")
def msg(n,b):
 return f"""Assalam-o-Alaikum {n},

LIBERTY AGRO CHEMICALS
Payment Reminder / Account Reference

According to our ledger, your remaining outstanding balance is Rs. {b:,.0f}/-.

Kindly clear the outstanding payment at your earliest convenience and share the payment confirmation with us.

Thank you for your cooperation.
Regards,
Liberty Agro Chemicals
Sukkur"""
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("Liberty Agro Chemicals - Dealer Payment Reminder"); self.geometry("1050x650")
  self.data=[]; self.build(); self.load(DATA)
 def build(self):
  tk.Label(self,text="LIBERTY AGRO CHEMICALS",font=("Arial",20,"bold")).pack(anchor="w",padx=15,pady=(15,0))
  tk.Label(self,text="Dealer Payment Reminder System",font=("Arial",11)).pack(anchor="w",padx=15)
  bar=tk.Frame(self); bar.pack(fill="x",padx=15,pady=12)
  tk.Button(bar,text="IMPORT CSV",command=self.imp,width=15).pack(side="left")
  tk.Button(bar,text="SEND ALL",command=self.all,width=15).pack(side="left",padx=8)
  tk.Label(bar,text="Search:").pack(side="left",padx=(15,5)); self.q=tk.StringVar(); self.q.trace_add("write",lambda *_:self.refresh())
  tk.Entry(bar,textvariable=self.q,width=30).pack(side="left")
  self.stat=tk.Label(self,font=("Arial",10,"bold")); self.stat.pack(anchor="w",padx=15)
  fr=tk.Frame(self); fr.pack(fill="both",expand=True,padx=15,pady=8)
  self.t=ttk.Treeview(fr,columns=("ac","name","phone","bal","send"),show="headings")
  for c,h,w in [("ac","A/c No",80),("name","Dealer Name",400),("phone","Mobile",150),("bal","Outstanding (Rs.)",180),("send","Action",100)]:
   self.t.heading(c,text=h); self.t.column(c,width=w)
  self.t.pack(side="left",fill="both",expand=True); ttk.Scrollbar(fr,command=self.t.yview).pack(side="right",fill="y")
  self.t.bind("<Double-1>",lambda e:self.send())
  tk.Button(self,text="SEND WHATSAPP FOR SELECTED DEALER",command=self.send,font=("Arial",10,"bold")).pack(pady=10)
 def load(self,p):
  with open(p,encoding="utf-8-sig") as f:self.data=[dict(x) for x in csv.DictReader(f)]
  self.refresh()
 def imp(self):
  p=filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
  if p:self.load(p)
 def refresh(self):
  q=self.q.get().lower(); self.cur=[d for d in self.data if q in d["name"].lower() or q in d["phone"] or q in d["account"]]
  self.t.delete(*self.t.get_children())
  for d in self.cur:self.t.insert("", "end",values=(d["account"],d["name"],d["phone"],f'{int(float(d["balance"])):,}',"SEND"))
  self.stat.config(text=f"Dealers: {len(self.data)}   |   Total Outstanding: Rs. {sum(int(float(x['balance'])) for x in self.data):,}   |   Showing: {len(self.cur)}")
 def selected(self):
  s=self.t.selection()
  if not s:return None
  ac=str(self.t.item(s[0],"values")[0]); return next((d for d in self.cur if d["account"]==ac),None)
 def send(self,d=None):
  d=d or self.selected()
  if not d:return messagebox.showinfo("Select Dealer","Please select a dealer.")
  p=phone(d["phone"])
  if not p:return messagebox.showwarning("No Mobile","No valid mobile number for "+d["name"])
  u="https://web.whatsapp.com/send?phone="+p+"&text="+urllib.parse.quote(msg(d["name"],int(float(d["balance"]))))
  webbrowser.open(u)
 def all(self):
  valid=[d for d in self.data if phone(d["phone"])]
  if not valid:return
  if messagebox.askyesno("Send All",f"Open WhatsApp for {len(valid)} dealers? You will press Send in WhatsApp for each message."):
   self.send(valid[0]); messagebox.showinfo("Send All Mode","First message opened. After sending, return here and click SEND for the next dealer.")
if __name__=="__main__":App().mainloop()
