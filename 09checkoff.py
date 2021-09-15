#!/usr/bin/env python
# coding: utf-8

# In[5]:


#!/usr/bin/env python
# coding: utf-8

# In[55]:


#!/usr/bin/env python
# coding: utf-8

# In[107]:


#!/usr/bin/env python3
"""6.009 Lab 8: Snek Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!
def evaluate_file(f_name,env=None):

    f = open(f_name,'r')
    expression=f.read()
#     print(parse(tokenize(expression)))

    return evaluate(parse(tokenize(expression)),env)
class Pair(object):
    def __init__(self,head,tail):
        self.head=head
        self.tail=tail
class environment(object):
    def __init__(self,parent=None):
        self.parent=parent
        self.bindings={}
    def bind(self,items):
        self.bindings[items[0]]=items[1]
        return items[1]
    def lookup(self,symbol,func=False):
        if symbol in self.bindings:
            return self.bindings[symbol]
        elif self.parent==None:
#             print(symbol)
            if not func:
                raise SnekNameError('variable does not exist in environment or parent environment!')
            else:
                raise SnekEvaluationError('Tried to call a non-existing function!')
        else:
            return self.parent.lookup(symbol)


class user_func:
    def __init__(self,parameters,operation,enclosing_env):
        self.parameters=parameters
        self.tree=operation
        self.enclosing_env=enclosing_env
        
    def evalu(self,func_env):
        return evaluate(self.tree,func_env)
###########################
# Snek-related Exceptions #
###########################


class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    def __init__(self, message=None):
        self.message=message

class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    def __init__(self, message=None):
        self.message=message
        
class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    def __init__(self, message=None):
        self.message=message

############################
# Tokenization and Parsing #
############################

def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x
        
def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    # split lines
    t1=source.splitlines()
    # delete comments
    t2=[part.partition(';')[0] for part in t1]
    # split by space
    t3=[part.split(' ') for part in t2]
    # flatten list and delete empty strings
    t4=[]
    for lst in t3:
        for item in lst:
            if item!='':
                t4.append(item)
#     print('t4 is',t4)
    #seperate parentethese
    t5=[]
    for string in t4:
        index=0
        while index<len(string):
            if string[index]=="(" or string[index]==")":
                t5.append(string[index])
                index+=1
            else:
                s=''
                while index<len(string) and (string[index]!="(" and string[index]!=")"):
                    s+=string[index]
                    index+=1
                t5.append(s)
    
    return t5

            
            

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    
    def parse_expression(index):
        if index>=len(tokens):
            raise SnekSyntaxError("parentheses mismatch!")
        s_expression=[]
        current=index
        length=0
        while current<len(tokens) and tokens[current]!=')':
            if tokens[current]=='(':
                s_exp,new_start=parse_expression(current+1)
                s_expression.append(s_exp)
                current=new_start
                length+=1
            else:
                s_expression.append(number_or_symbol(tokens[current]))
                current+=1
                length+=1
            if current==len(tokens) and tokens[current-1]!=")":
                raise SnekSyntaxError("parentheses mismatch!")
        if tokens[index]=="define":
            if length!=3:
                raise SnekSyntaxError("define must be well formed, num of arguments wrong!")
            if not isinstance(s_expression[1],(list,str)):
                raise SnekSyntaxError("define must be well formed, object name wrong!")
            elif isinstance(s_expression[1],list):
                if len(s_expression[1])==0:
                    raise SnekSyntaxError("function must have a name!")
                for s in s_expression[1]:
                    if not isinstance(s,str):
                        raise SnekSyntaxError("define must be well formed, function name or parameter is not string!")
        if tokens[index]=="lambda" :
            if (length!=3 or type(s_expression[1])!=list):
                raise SnekSyntaxError("user function must be well formed, num of arguments wrong!")
            else:
                for s in s_expression[1]:
                    if not isinstance(s,str):
                        raise SnekSyntaxError("function must be well formed, function parameter is not string!")
        if tokens[index]=="if" :
            if (length!=4):
                raise SnekSyntaxError("if expression must be of the right length")
      

        return (s_expression,current+1)
        
    result=[]
    current=0
#     if tokens[current]!="(":
#         raise SnekSyntaxError("must start with parenthsis!")
    while current<len(tokens):
        if tokens[current]==')':
            raise SnekSyntaxError("parentheses mismatch!")
        
        elif tokens[current]=='(':
            s_expression,new_start=parse_expression(current+1)
            current=new_start
            result.append(s_expression)
            
        elif tokens[current]=='define' or tokens[current]=='lambda':
            raise SnekSyntaxError("define/lambda must be well formed, missing parenthese!")
        
        
        else:
            result.append(number_or_symbol(tokens[current]))
            current+=1
    

    return result[0]


######################
# Built-in Functions #
######################


def mul(args):
    if len(args)==0:
        return 1
    elif len(args)==1:
        return args[0]
    else:
        print(args[0])
        return args[0]*mul(args[1:])
    
def div(args):
    if len(args)==0:
        raise exception("at least one argument for division!")
    elif len(args)==1:
        return 1/args[0]
    else:
        result=args[0]
        for divisor in args[1:]:
            result=result/divisor
        return result
def func_not(args):
    return (not args[0])
def return_head(pair):
#     if len(pair)!=1:
#         raise SnekEvaluationError("tried to get head with wrong number of arguments passed in!")
    return pair[0].head
def return_tail(pair):
#     if len(pair)!=1:
#         raise SnekEvaluationError("tried to get tail with wrong number of arguments passed in!")
    return pair[0].tail
def lst_len(lst):
#     lst=lst[0]
#     print(lst)
    
    lst=lst[0]    
    if lst==[]:
        return 0
    if not isinstance(lst, Pair):
        raise SnekEvaluationError("Not a valid pair!")
    def count_len(lst):
        if (not isinstance(lst.tail, Pair)) and lst.tail!=[]:
            raise SnekEvaluationError("Pair is not a list!")
        if lst.tail==[]:
            return 1
        else:
            return count_len(lst.tail)+1
    return count_len(lst)

def nth(args):
    pr=args[0]
    index=args[1]
    if pr==[]:
        raise SnekEvaluationError("empty list!")
    if index==0:
        return pr.head

    if not check_is_lst(pr):
        raise SnekEvaluationError("pair is not a list, only can return index 0!")
    def get_nth(pr,index):
        if index==0:
            return pr.head
        
        else:
            if not isinstance(pr,Pair):
                raise SnekEvaluationError("list index out of range!")
            return get_nth(pr.tail,index-1)
    return get_nth(pr,index)

def check_is_lst(pr):
    current=pr

    while True:
        if isinstance(current.tail,Pair):
            current=current.tail
        elif current.tail==[]:
            return True
        else:
            return False
        
def concat(lists):
    toappend=[]
    if lists==[]:
        return evaluate("nil")
    if len(lists)==1:
        return lists[0]
    for index in range(len(lists)-1,0,-1):
        if lists[index]==[]:
            pass
        else:
            if not isinstance(lists[index],Pair):
                raise SnekEvaluationError("can only concat pairs!")
            elif index==len(lists)-1: toappend=lists[index]   
        if lists[index-1]==[]:
            if index-1==0:
                return toappend
            else:
                continue   
        newlist=copy_lst(lists[index-1])
        current=newlist
        while current.tail!=[]:
            current=current.tail
            if not isinstance(current,Pair):
                raise SnekEvaluationError("pair is not a list!")
        current.tail=copy_lst(toappend)
        toappend=newlist
    return newlist


def copy_lst(lst):
    if lst==[]:
        return []
    
    else:
        current=lst
        newpair=Pair(lst.head,[])
        current_copy=newpair
        while isinstance(current.tail,Pair):
            current=current.tail
            current_copy.tail=Pair(current.head,[])
            current_copy=current_copy.tail
        if current.tail!=[]:
            raise SnekEvaluationError("pair is not a list!")
        return newpair
    
    
def func_map(args):
    func=args[0]
    lst=args[1]
    if lst!=[] and ((not isinstance(lst,Pair)) or (not check_is_lst(lst))):
        raise SnekEvaluationError("can only map onto a list!")
    
    if lst==[]:
        return []
    
    elif isinstance(func, user_func):
        current=lst
        func_env=environment(func.enclosing_env)
        func_env.bindings[func.parameters[0]]=current.head
        newpair=Pair(func.evalu(func_env),[])
        current_copy=newpair
        while isinstance(current.tail,Pair):
            current=current.tail
            func_env.bindings[func.parameters[0]]=current.head
            current_copy.tail=Pair(func.evalu(func_env),[])
            current_copy=current_copy.tail
    else:
        if func not in snek_builtins.values():
            raise SnekEvaluationError("can only map with a function!")
        current=lst
#         print(func)
        newpair=Pair(func([current.head]),[])
        current_copy=newpair
        while isinstance(current.tail,Pair):
            current=current.tail
            current_copy.tail=Pair(func([current.head]),[])
            current_copy=current_copy.tail

    return newpair
    
def func_filter(args):
    func=args[0]
    lst=args[1]
    #type checking
    if not isinstance(func,user_func):
        raise SnekEvaluationError("can only filter through a function!")
    if lst!=[] and ((not isinstance(lst,Pair)) or (not check_is_lst(lst))):
        raise SnekEvaluationError("can only filter a list!")
    if lst==[]:
        return []
    current=lst
    counter=0
    result=Pair([],[])
    new_pair=result
    while isinstance(current,Pair):
        func_env=environment(func.enclosing_env)
        func_env.bindings[func.parameters[0]]=current.head
        if func.evalu(func_env)==True:
            if counter!=0:
                new_pair.tail=Pair(current.head,[])
                new_pair=new_pair.tail
            else:
                new_pair.head=current.head
            counter+=1
        current=current.tail
    if counter==0:
        return []
    return result


def reduce(args):
    func=args[0]
    lst=args[1]
    initial=args[2]
    result=initial
    current=lst
    if lst!=[] and ((not isinstance(lst,Pair)) or (not check_is_lst(lst))):
        raise SnekEvaluationError("can only reduce a list!")
   
    if lst==[]:
        return initial
    elif isinstance(func, user_func):    
        while isinstance(current,Pair):
            func_env=environment(built_in)
            func_env.bindings[func.parameters[0]]=result
            func_env.bindings[func.parameters[1]]=current.head
            result=func.evalu(func_env)
            current=current.tail
        return result
    else:
        if func not in snek_builtins.values():
            raise SnekEvaluationError("can only reduce with a function!")
        while isinstance(current,Pair):
            result=func([result,current.head])
            current=current.tail
        return result

def begin(args):
    return args[-1]
            
#     def flatten_list(lst):
#         result=[]
#         while True:
#             if lst==[]:
#                 return []

#             else:
#                 result.append(lst.head)
#                 if lst.tail==[]:
#                     return result
#                 lst=lst.tail
#     full_lst=[]
#     for lst in lists:
# #         print lst
#         full_lst.extend(flatten_list(lst))
#     def make_pair(lst):
#         if len(lst)==0:
#             return []
#         if len(lst)==1:
#             return Pair(lst[0],[])
#         else:
#             return Pair(lst[0],make_pair(lst[1:]))
#     return make_pair(full_lst)

built_in=environment()
global_env=environment(built_in)

snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
    "define": global_env.bind,
#     "and":func_and,
#     "or":func_or,
    "#t":True,
    "#f":False,
    "not":func_not,
    "head":return_head,
    "tail":return_tail,
    "nil":[],
    "length":lst_len,
    "nth":nth,
    "concat":concat,
    "map":func_map,
    "filter": func_filter,
    "reduce":reduce,
    "begin":begin
    

    
#     "lambda":temp_func
}

###########################
# initialize environments #
###########################

for operator in snek_builtins:
    built_in.bind([operator,snek_builtins[operator]])

##############
# Evaluation #
##############




def evaluate(tree,env=None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    userfunction=False
    if env==None:
#         env=environment(built_in)
        env=global_env
        env.bindings["define"]=env.bind
    if tree==[]:
        raise SnekEvaluationError("tree is empty!")
    if isinstance(tree,int):
        return tree
    elif isinstance(tree,float):
        return tree
    elif isinstance(tree,str):
        return env.lookup(tree)

    elif tree=="nil":
        return []
    elif tree=="#f":
        return False
    elif tree=="#t":
        return True
    elif tree[0]=="lambda":
        return user_func(tree[1],tree[2],env)
    elif isinstance(tree[0],list):
        func=evaluate(tree[0],env)
        if isinstance(func,user_func):
            userfunction=True
            func_env=environment(func.enclosing_env)
#####################################
####special forms from lab9 start####
#####################################
#     elif tree[0]=="length":
        
    elif tree[0]=="list":
        if len(tree)==1:
            return evaluate("nil",env)
        elif len(tree)==2:
            return Pair(evaluate(tree[1],env),evaluate("nil",env))
        else:
            return Pair(evaluate(tree[1],env),evaluate(["list",*tree[2:]],env))
               
#     elif tree[0]=="head" or tree[0]=="tail":
#         if not isinstance(evaluate(tree[1],env),Pair):
#             raise SnekEvaluationError("tried to get head or tail from wrong type of data!")
            
#     elif tree[0]=="map":
#         func=evaluate(,env)
    elif tree[0]=="pair":
        if len(tree)!=3:
                raise SnekEvaluationError("tried to intialize pair with the wrong number of arguments passed in!")
        return Pair(evaluate(tree[1],env),evaluate(tree[2]))
    elif tree[0]=="del":
#         print(tree[1])
        if tree[1] not in env.bindings:
            raise SnekNameError("is not in local env")
        result=env.bindings[tree[1]]
        del env.bindings[tree[1]]
        return result
    elif tree[0]=="let":
        new_env=environment(env)
        new_env.bindings["define"]=new_env.bind
        for v in tree[1]:
            evaluate(['define']+[v[0]]+[v[1]],new_env)
        return evaluate(tree[2],new_env)
    elif tree[0]=="set!":
        expr=tree[2]
        vari=tree[1]
        result=evaluate(expr,env)
        def bind_var(var,env):
            if var in env.bindings:
                env.bindings[var]=result
                return result
            else:
                if env.parent==None:
                    raise SnekNameError("varibale does not exist for set bang!")
                env=env.parent
                bind_var(var,env)
        bind_var(vari,env)
        return result
    
    elif tree[0]=="if":
        if evaluate(tree[1],env)==True:
            return evaluate(tree[2],env)
        else:
            return evaluate(tree[3],env)
    elif tree[0]=="=?":
        for i in range(1,len(tree)-1,1):
            if evaluate(tree[i],env)!=evaluate(tree[i+1],env):
                return False
        return True
    elif tree[0]==">":
        for i in range(1,len(tree)-1,1):
            if evaluate(tree[i],env)<=evaluate(tree[i+1],env):
                return False
        return True
    elif tree[0]=="<":
        for i in range(1,len(tree)-1,1):
            if evaluate(tree[i],env)>=evaluate(tree[i+1],env):
                return False
        return True
    elif tree[0]==">=":
        for i in range(1,len(tree)-1,1):
            if evaluate(tree[i],env)<evaluate(tree[i+1],env):
                return False
        return True
    elif tree[0]=="<=":
        for i in range(1,len(tree)-1,1):
            if evaluate(tree[i],env)>evaluate(tree[i+1],env):
                return False
        return True
    elif tree[0]=="and":
        for expression in tree[1:]:
            if evaluate(expression,env)==False:
                return False
        return True
    elif tree[0]=="or":
        for expression in tree[1:]:
            if evaluate(expression,env)==True:
                return True
        return False

 ####special forms from lab9 end####
    elif isinstance(tree[0],str):
        func=env.lookup(tree[0])
        if tree[0]=="not" and (not isinstance(func,user_func)):
            if (len(tree)!=2):
                raise SnekEvaluationError("not expression must be of the right length")
        if (tree[0]=="head" or tree[0]=="tail") and (not isinstance(func,user_func)):
            if len(tree)!=2:
                raise SnekEvaluationError("tried to get head with wrong number of arguments passed in!")
            if not isinstance(evaluate(tree[1],env),Pair):
                raise SnekEvaluationError("tried to get head or tail from wrong type of data!")
        if tree[0]=="define":
            if isinstance(tree[1],list):
                func_name=tree[1][0]
                if len(tree[1])>1:
                    paras=tree[1][1:]
                    operation=tree[2]
                    values=[func_name, user_func(paras,operation,env)]
                    return func(values)
                else:
                    paras=[]
                    operation=tree[2]
                    values=[func_name, user_func(paras,operation,env)]
                    return func(values)

        if isinstance(func,user_func):
            userfunction=True
            func_env=environment(func.enclosing_env)
            func_env.bindings["define"]=func_env.bind

    else:
        raise SnekEvaluationError('not evaluable!')
    values=[]
    for i in range(1,len(tree),1):

        if isinstance(tree[i],list):
            value=evaluate(tree[i],env)
            values.append(value)
        elif isinstance(tree[i],str) and (tree[0]!="define" or i!=1):
#             print("here?")
            value=env.lookup(tree[i])
            values.append(value)
        else:
            values.append(tree[i])
    if userfunction :
#         print('is user function!')
#         print(env.bindings)
        index=0
        if len(values)!=len(func.parameters):
            raise SnekEvaluationError("the number of parameters does not match")
        for p in func.parameters:
            func_env.bindings[p]=values[index]
            index+=1
#         if type(tree[0])!=list:
#             print('did this!')
#             func_env.bindings[tree[0]]=func
#         print(func_env.bindings)
        return func.evalu(func_env)
    else:
        return func(values)

def result_and_env(tree,env=None):
    if env==None:
        env=environment(built_in)
        env.bindings["define"]=env.bind
    return (evaluate(tree,env), env)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    listinput=''
    counter=0
    while True:
        print('in>')
        lispinput=input()
        if lispinput=='QUIT':
            break
        if counter==0:
            try:
                output,env=result_and_env(parse(tokenize(lispinput)))   
            except SnekError as err:
                print(type(err),":",err.message)
        else:
            try:
                output,env=result_and_env(parse(tokenize(lispinput)),env)
            except SnekError as err:
                print(type(err),":",err.message)
        counter+=1
        print('out>',output)

    pass


# In[ ]:





# In[ ]:





# In[ ]:


# In[ ]:




