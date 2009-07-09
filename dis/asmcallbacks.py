#!/usr/bin/python

def getOperands(line):
    line = line.replace("%", "")
    data = line.split(" ")
    data = data[len(data)-1]
    ops = data.split(",")

    if len(ops) == 2:
        op1 = ops[0]
        op2 = ops[1]

        return op1, op2

def warningCallback(block, line, function, prevInstruction):
    
    if function == "getenv":
        return getenvCallback(block, line, function, prevInstruction)
    elif function in ["printf", "puts"]:
        return printfCallback(block, line, function, prevInstruction)

def codeCallback(block, line, func, prevInstruction):
    params = line.split(" ")
    ops = getOperands(line)

    if not ops:
        ops = line.split(" ")
        #return

    if params[0] == "add":
        return "%s += %s" % (ops[1], ops[0])
    elif params[0] == "sub":
        return "%s -= %s" % (ops[1], ops[0])
    elif params[0] in ["mov", "movl", "movs", "movsb", "movsw"]:
        return "%s = %s" % (ops[1], ops[0])
    elif params[0] in ["mul", "imul", "fmul", "fimul"]:
        return "%s *= %s" % (ops[1], ops[0])
    elif params[0] == "inc":
        return "%s++" % ops[0]
    elif params[0] == "dec":
        return "%s--" % ops[0]
    elif params[0] == "shl":
        return "%s = %s << %s" % (ops[1], ops[1], ops[0])
    elif params[0] == "shr":
        return "%s = %s >> %s" % (ops[1], ops[1], ops[0])
    elif params[0] == "div":
        return "eax = eax / %s" % ops[0]
    elif params[0] == "ret":
        return "return"
    elif params[0] == "call":
        return "%s()" % ops[4].replace("<", "").replace(">", "")
    elif params[0][0] == "j":
        if params[0] == "jmp":
            return "goto %s" % ops[0]
            
        return

        if params[0] == "je":
            print "SALTO SI IGUAL"
        elif params[0] == "jg":
            print "SALTO SI MAYOR"
        elif params[0] == "jge":
            print "SALTO SI MAYOR O IGUAL"
        elif params[0] == "jl":
            print "SALTO SI MENOR"
        elif params[0] == "jle":
            print "SALTO SI MENOR O IGUAL"
        elif params[0] == "jne":
            print "SALTO SI DIFERENTE"
        elif params[0] == "jng":
            print "SALTO SI NO MAYOR"
        elif params[0] == "jnge":
            print "SALTO SI NO MAYOR O IGUAL"
        elif params[0] == "jnl":
            print "SALTO SI NO MENOR"
        elif params[0] == "jnle":
            print "SALTO SI NO MENOR O IGUAL"
        elif params[0] == "jnz":
            print "SALTO SI NO CERO"
        elif params[0] == "jz":
            print "SALTO SI CERO"
        else:
            return
    else:
        return

    print line
    raw_input()

def printfCallback(block, line, function, prevInstruction):

    clearIns = prevInstruction.lower().replace(" ", "")
    if clearIns.find("mov%eax,(%esp)") > -1 or clearIns.find("push%") > -1:
        return "First parameter of the printf call is not a format string. Check for format strings."

def getenvCallback(block, line, function, prevInstruction):
    if len(block) > 1:
        instruction = prevInstruction.split(" ")[1].lower()

        if instruction == "push" or instruction.find("mov") > -1:
            asmLine = prevInstruction.split(";'")

            if len(asmLine) > 1:
                return "Check the environment variable '%s for overflows, format strings, etc..." % asmLine[1]

