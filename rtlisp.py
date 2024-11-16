def dfs(e,p,dep=0):
    def bl(x):
        return 't' if x else []
    if type(e)==type(''):
        return p[e] if e in p else e
    op=dfs(e[0],p,dep+1)
    if op=='lambda':
        return e
    if op=='quote':
        return e[1]
    if op=='cond':
        for i in e[1:]:
            if dfs(i[0],p,dep+1)=='t':
                return dfs(i[1],p,dep+1)
    if type(op)==type([]) and len(op) and op[0]=='lambda':
        return dfs(op[2],{**p,
            **dict(zip(op[1],[dfs(i,p,dep+1) for i in e[1:]]))},dep+1)
    if op=='atom':
        r=dfs(e[1],p,dep+1)
        return bl(r==[] or type(r)==type(''))
    if op=='eq':
        return bl(dfs(e[1],p,dep+1)==dfs(e[2],p,dep+1))
    if op=='car':
        return dfs(e[1],p,dep+1)[0]
    if op=='cdr':
        return dfs(e[1],p,dep+1)[1:]
    if op=='cons':
        return [dfs(e[1],p,dep+1)]+dfs(e[2],p,dep+1)
    raise Exception(py2l(e)+'\n'+str(p))

def l2py(l):
    r=[None]
    s=[r]
    for i in l:
        if i=='(':
            if s[-1][-1]==None:
                s[-1].pop()
            s[-1].append([None])
            s[-1].append(None)
            s.append(s[-1][-2])
        elif i==')':
            if s[-1][-1]==None:
                s[-1].pop()
            s.pop()
        elif i in ' \t\r\n':
            if s[-1][-1]!=None:
                s[-1].append(None)
        else:
            if s[-1][-1]==None:
                s[-1][-1]=i
            else:
                s[-1][-1]+=i
    return r[:-1]

def py2l(p):
    if type(p)==type(''):
        return p+' '
    return '( '+''.join([py2l(i) for i in p])+') '

def lisp(s,f):
    f('compiling')
    e=l2py(s)
    for i in range(len(e)):
        f('running')
        e[i]=dfs(e[i],{})
        f('done')
        e[i]=py2l(e[i])
    return '\n'.join(e)

################################################################################

from time import time
import tkinter as tk
import tkinter.filedialog as fd

def log(s):
    outbox.insert('end',s)
    outbox.see('insert')
    outbox.update()

def go(arg):
    try:
        if len(outbox.get(1.0,'end'))>1:
            log('\n'+'-'*30+'\n\n')
        def f(x):
            log('['+str(round((time()-p)*1000)).rjust(5)+'ms]\t'+x+'\n')
        p=time()
        r=lisp(inbox.get(1.0,'end'),f)
        log('\n'+r+'\n')
    except Exception as e:
        outbox.insert('end','\n:(  Error! Aborted.\n\nDetails:\n'+str(e)+'\n')
    return 'break'

def fileopen(arg):
    fn=fd.askopenfilename(title='Open...',
        filetypes=[('Lisp files','*.lsp *.lisp'),('Text files','*.txt'),
        ('All files','*')])
    if not fn:
        return
    try:
        with open(fn,mode='r',encoding='utf-8') as f:
            s=f.read()
            inbox.delete(1.0,'end')
            inbox.insert(1.0,s)
    except:
        log('\nCannot open '+fn+'!\n')
    else:
        log('\nOpened '+fn+'\n')
    return 'break'

def filesave(arg):
    fn=fd.asksaveasfilename(title='Save as...',
        filetypes=[('Lisp files','*.lsp *.lisp'),('Text files','*.txt'),
        ('All files','*')])
    if not fn:
        return
    try:
        with open(fn,mode='w',encoding='utf-8') as f:
            f.write(inbox.get(1.0,'end')[:-1])
    except:
        log('\nCannot save as '+fn+'!\n')
    else:
        log('\nSaved as '+fn+'\n')
    return 'break'

def f1help(arg):
    inbox.insert(1.0,"""

Rtlisp is a variant of lisp. It ONLY supports:

  atom quote eq car cdr cons cond lambda

You might be familiar with them; for more info, see:

  https://paulgraham.com/rootsoflisp.html

Warning:

  1. Single quote won't be analyzed as quote!
     Use (quote ...) instead.

  2. Comments aren't supported!

  3. Remember to save before exiting!

Shortcut keys:

  ^R\tRun the script;

  ^O\tOpen a script file;

  ^S\tSave the script;

  F1\tHelp! I need help!

:) Good Luck~

    """[2:-4]+'-'*80+'\n\n')
    inbox.see(1.0)
    log('\nHere you are.\n')
    return 'break'

def intab(arg):
    if inbox.tag_ranges('sel'):
        return None
    s=inbox.get(1.0,'insert')
    inbox.insert('insert',' '*(4-(len(s)-s.rfind('\n')-1)%4))
    inbox.see('insert')
    return 'break'

def inbsp(arg):
    if inbox.tag_ranges('sel'):
        return None
    s=inbox.get(1.0,'insert')
    p=inbox.index('insert').split('.')
    if p[1]=='0':
        return None
    l1=(len(s)-s.rfind('\n')-2)%4+1
    l2=max(len(s)-len(s.strip()),1)
    p[1]=str(int(p[1])-min(l1,l2))
    inbox.delete('.'.join(p),'insert')
    inbox.see('insert')
    return 'break'

def inetr(arg):
    if inbox.tag_ranges('sel'):
        return None
    s=inbox.get(1.0,'insert')
    s=s[s.rfind('\n')+1:]
    inbox.insert('insert','\n'+' '*(len(s)-len(s.lstrip())))
    inbox.see('insert')
    return 'break'

rt=tk.Tk()
rt.title('rtlisp')
rt.geometry("812x450")

inscr=tk.Scrollbar(rt)
inbox=tk.Text(rt,yscrollcommand=inscr.set,undo=1)
inscr.config(command=inbox.yview)
outscr=tk.Scrollbar(rt)
outbox=tk.Text(rt,yscrollcommand=outscr.set,width=30)
outscr.config(command=outbox.yview)
outscr.pack(fill='y',side='right')
outbox.pack(fill='y',side='right')
inscr.pack(fill='y',side='right')
inbox.pack(fill='both',expand=1)

rt.bind('<Control-r>',go)
rt.bind('<Control-o>',fileopen)
rt.bind('<Control-s>',filesave)
rt.bind('<F1>',f1help)

inbox.bind('<Tab>',intab)
inbox.bind('<BackSpace>',inbsp)
inbox.bind('<Return>',inetr)

inbox.insert(1.0,"""((lambda (subst)
    (subst (quote m) (quote b) (quote (a b (a b c) d)))
)
    (lambda (x y z)
        (cond
            ((atom z)
                (cond
                    ((eq z y)
                        x
                    )
                    ((quote t)
                        z
                    )
                )
            )
            ((quote t)
                (cons (subst x y (car z)) (subst x y (cdr z)))
            )
        )
    )
)""")
outbox.insert(1.0,"""Welcome to rtlisp!

:)

Don't panic, F1 = help.
""")

rt.mainloop()
