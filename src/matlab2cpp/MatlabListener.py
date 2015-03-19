"""
Build token tree from matlab-code
"""

from antlr4 import *

import collection as col

class MatlabListener(ParseTreeListener):

    def enterProgram(self, ctx):
        ctx.program = col.Program()
        ctx.program["backend"] = "program"
        ctx.program["names"] = []

        includes = col.Includes(ctx.program)
        includes["backend"] = "program"
        includes["names"] = []

        i1 = col.Include(includes, "armadillo")
        i1["value"] = "#include <armadillo>"
        i1["backend"] = "program"

        i2 = col.Include(includes, "usingarma")
        i2["value"] = "using namespace arma;"
        i2["backend"] = "program"

        func = col.Func(ctx.program, "main")
        declares = col.Declares(func)
        returns = col.Returns(func)
        params = col.Params(func)

        func["backend"] = "func_return"
        declares["backend"] = "func_return"
        returns["backend"] = "func_return"
        params["backend"] = "func_return"

        declares["names"] = []
        returns["names"] = ["_retval"]
        params["names"] = ["argc", "argv"]

        var = col.Var(returns, "_retval")
        var.type("int")
        var["backend"] = "int"
        var.declare(var)

        argc = col.Var(params, "argc")
        argc.type("int")
        argc["backend"] = "int"

        argv = col.Var(params, "argv")
        argv.type("char")
        argv["backend"] = "char"
        argv["pointer"] = 2

        ctx.node = func

    def exitProgram(self, ctx):
        ctx.program["names"].append("main")
        cs = ctx.program.children
        ctx.program.children = cs[:1] + cs[2:] + cs[1:2]

        if len(ctx.node) != 4:
            block = col.Block(ctx.node)
            block["backend"] = "code_block"

        block = ctx.node[3]
        assign = col.Assign(block)
        var = col.Var(assign, "_retval")
        var.type("int")
        i = col.Int(assign, "0")
        i.type("int")
        i["backend"] = "int"

    def enterFunction(self, ctx):
        program = ctx.parentCtx.node.program
        name = ctx.ID().getText()
        program["names"].append(name)
        ctx.node = col.Func(program, name)
        declares = col.Declares(ctx.node)
        declares["names"] = []

        if ctx.function_returns() is None:
            returns = col.Returns(ctx.node)
            returns["names"] = []

            if ctx.function_params() is None:
                params = col.Params(ctx.node)
                params["names"] = []

    def exitFunction(self, ctx):

        node = ctx.node

        if len(node[1]) == 1:
            node["backend"] = "func_return"
            node[0]["backend"] = "func_return"
            node[1]["backend"] = "func_return"
            node[2]["backend"] = "func_return"
        else:
            node["backend"] = "func_returns"
            node[0]["backend"] = "func_returns"
            node[1]["backend"] = "func_returns"
            node[2]["backend"] = "func_returns"

        for var in node[1][:]:
            var.declare()

    def enterFunction_returns(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Returns(pnode)
        ctx.node["names"] = []

        count = ctx.getChildCount()
        for n in xrange((count-2)/2 or 1):
            name = ctx.ID(n).getText()
            col.Var(ctx.node, name)
            ctx.node["names"].append(name)

        if ctx.parentCtx.function_params() is None:
            params = col.Params(pnode)
            params["names"] = []

    def exitFunction_returns(self, ctx):
        pass

    def enterFunction_params(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Params(pnode)
        ctx.node["names"] = []
        for n in xrange((ctx.getChildCount()+1)/2):
            name = ctx.ID(n).getText()
            col.Var(ctx.node, name)
            ctx.node["names"].append(name)

    def exitFunction_params(self, ctx):
        pass

    def enterCodeline(self, ctx):
        ctx.node = ctx.parentCtx.node

    def exitCodeline(self, ctx):
        pass

    def enterCodeblock(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Block(pnode)
        ctx.node["backend"] = "code_block"

    def exitCodeblock(self, ctx):
        pass

    def enterBranch(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Branch(pnode)
        ctx.node["backend"] = "code_block"

    def exitBranch(self, ctx):
        pass

    def enterBranch_if(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.If(pnode)
        ctx.node["backend"] = "code_block"

    def exitBranch_if(self, ctx):
        pass

    def enterBranch_elif(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Elif(pnode)
        ctx.node["backend"] = "code_block"

    def exitBranch_elif(self, ctx):
        pass

    def enterBranch_else(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Else(pnode)
        ctx.node["backend"] = "code_block"

    def exitBranch_else(self, ctx):
        pass

    def enterCondition(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Cond(pnode)
        ctx.node["backend"] = "code_block"

    def exitCondition(self, ctx):
        pass

    def enterSwitch_(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Switch(pnode)
        ctx.node["backend"] = "code_block"

    def exitSwitch_(self, ctx):
        pass

    def enterSwitch_case(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Case(pnode)
        ctx.node["backend"] = "code_block"

    def exitSwitch_case(self, ctx):
        pass

    def enterSwitch_otherwise(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Otherwise(pnode)
        ctx.node["backend"] = "code_block"

    def exitSwitch_otherwise(self, ctx):
        pass

    def enterLoop(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.For(pnode)
        col.Var(ctx.node, ctx.ID().getText()).declare()
        ctx.node["backend"] = "code_block"

    def exitLoop(self, ctx):
        pass

#      def enterLoop_range(self, ctx):
#          pnode = ctx.parentCtx.node
#          col.Var(pnode, ctx.ID().getText()).declare()
#          ctx.node = pnode
#          ctx.node["backend"] = "code_block"

    def enterWloop(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.While(pnode)
        ctx.node["backend"] = "code_block"

    def exitWloop(self, ctx):
        pass

    def enterTry_(self, ctx):
        pnode = ctx.parentCtx.node
        node = col.Tryblock(pnode)
        ctx.node = col.Try(node)
        ctx.node["backend"] = "code_block"

    def exitTry_(self, ctx):
        pass

    def enterCatchid(self, ctx):
        ppnode = ctx.parentCtx.parentCtx.node
        ctx.node = col.Catch(ppnode, ctx.ID().getText())
        ctx.node["backend"] = "code_block"

    def exitCatchid(self, ctx):
        pass

    def enterCatch_(self, ctx):
        ppnode = ctx.parentCtx.parentCtx.node
        ctx.node = col.Catch(ppnode)
        ctx.node["backend"] = "code_block"

    def exitCatch_(self, ctx):
        pass

    def enterStatement(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Statement(pnode)
        ctx.node["backend"] = "code_block"

    def exitStatement(self, ctx):
        pass

    def enterAssign(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Assign(pnode)
        col.Var(ctx.node, ctx.ID().getText()).declare()
        ctx.node["backend"] = "unknown"

    def exitAssign(self, ctx):
        pass

    def enterAssigns(self, ctx):
        pnode = ctx.parentCtx.node
        assigns = col.Assigns(pnode)
        assigns["backend"] = "code_block"

        assigned = col.Assigned(assigns)
        assigned["backend"] = "code_block"
        for i in xrange((ctx.getChildCount()-2)/2):
            col.Var(assigned, ctx.ID(i).getText()).declare()

        ctx.node = assigns

    def exitAssigns(self, ctx):
        name = ctx.node[1]["name"]
        if name:
            ctx.node["name"] = name

    def enterSet1(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Set(pnode, ctx.ID().getText())
        ctx.node.declare()
        ctx.node["backend"] = "unknown"

    def exitSet1(self, ctx):
        pass

    def enterSet2(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Set2(pnode, ctx.ID().getText())
        ctx.node.declare()
        ctx.node["backend"] = "unknown"

    def exitSet2(self, ctx):
        pass

    def enterSet3(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Set3(pnode, ctx.ID().getText())
        ctx.node.declare()
        ctx.node["backend"] = "unknown"

    def exitSet3(self, ctx):
        pass

    def enterSets(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Sets(pnode)
        ctx.node["backend"] = "code_block"

    def exitSets(self, ctx):
        pass

    def enterExpr(self, ctx):
        ctx.node = ctx.parentCtx.node

    def exitExpr(self, ctx):
        pass

    def enterInfix(self, ctx):

        print dir(ctx)
        opr = ctx.OPR().getText()
        parent = ctx.parentCtx
        if hasattr(parent, "opr") and opr == parent.opr:
            ctx.node = parent.node
        else:
            pnode = parent.node

    def enterLor(self, ctx):
        if ctx.parentCtx.node["class"] == "Lor":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Lor(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitLor(self, ctx):
        pass


    def enterLand(self, ctx):
        if ctx.parentCtx.node["class"] == "Land":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Land(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitLand(self, ctx):
        pass


    def enterBor(self, ctx):
        if ctx.parentCtx.node["class"] == "Bor":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Bor(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitBor(self, ctx):
        pass


    def enterBand(self, ctx):
        if ctx.parentCtx.node["class"] == "Band":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Band(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitBand(self, ctx):
        pass


    def enterEq(self, ctx):
        if ctx.parentCtx.node["class"] == "Eq":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Eq(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitEq(self, ctx):
        pass


    def enterLe(self, ctx):
        if ctx.parentCtx.node["class"] == "Le":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Le(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitLe(self, ctx):
        pass


    def enterGe(self, ctx):
        if ctx.parentCtx.node["class"] == "Ge":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Ge(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitGe(self, ctx):
        pass


    def enterLt(self, ctx):
        if ctx.parentCtx.node["class"] == "Lt":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Lt(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitLt(self, ctx):
        pass


    def enterGt(self, ctx):
        if ctx.parentCtx.node["class"] == "Gt":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Gt(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitGt(self, ctx):
        pass


    def enterNe(self, ctx):
        if ctx.parentCtx.node["class"] == "Ne":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Ne(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitNe(self, ctx):
        pass


    def enterColon(self, ctx):
        if ctx.parentCtx.node["class"] == "Colon":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Colon(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitColon(self, ctx):
        pass


    def enterDiv(self, ctx):
        if ctx.parentCtx.node["class"] == "Div":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Div(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitDiv(self, ctx):
        pass


    def enterEldiv(self, ctx):
        if ctx.parentCtx.node["class"] == "Eldiv":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Eldiv(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitEldiv(self, ctx):
        pass


    def enterRdiv(self, ctx):
        if ctx.parentCtx.node["class"] == "Rdiv":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Rdiv(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitRdiv(self, ctx):
        pass


    def enterElrdiv(self, ctx):
        if ctx.parentCtx.node["class"] == "Elrdiv":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Elrdiv(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitElrdiv(self, ctx):
        pass


    def enterMul(self, ctx):
        if ctx.parentCtx.node["class"] == "Mul":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Mul(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitMul(self, ctx):
        pass


    def enterElmul(self, ctx):
        if ctx.parentCtx.node["class"] == "Elmul":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Elmul(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitElmul(self, ctx):
        pass


    def enterExp(self, ctx):
        if ctx.parentCtx.node["class"] == "Exp":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Exp(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitExp(self, ctx):
        pass


    def enterElexp(self, ctx):
        if ctx.parentCtx.node["class"] == "Elexp":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Elexp(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitElexp(self, ctx):
        pass


    def enterPlus(self, ctx):
        if ctx.parentCtx.node["class"] == "Plus":
            ctx.node = ctx.parentCtx.node
        else:
            ctx.node = col.Plus(ctx.parentCtx.node)
            ctx.node["backend"] = "expression"

    def exitPlus(self, ctx):
        pass


    def enterMinus(self, ctx):
        ctx.node = col.Neg(ctx.parentCtx.node)
        ctx.node["backend"] = "expression"

    def exitMinus(self, ctx):
        pass


    def enterNegate(self, ctx):
        ctx.node = col.Not(ctx.parentCtx.node)
        ctx.node["backend"] = "expression"

    def exitNegate(self, ctx):
        pass


    def enterIfloat(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Ifloat(pnode, ctx.getText())
        ctx.node["backend"] = "ifloat"

    def exitIfloat(self, ctx):
        pass

    def enterFloat(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Float(pnode, ctx.getText())
        ctx.node.type("float")
        ctx.node["backend"] = "float"

    def exitFloat(self, ctx):
        pass

    def enterEnd(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.End(pnode)
        ctx.node["backend"] = "expression"

    def exitEnd(self, ctx):
        pass

    def enterGet1(self, ctx):
        pnode = ctx.parentCtx.node
        name = ctx.ID().getText()
        ctx.node = col.Get(pnode, name)
        ctx.node["backend"] = "unknown"

    def exitGet1(self, ctx):
        pass

    def enterGet2(self, ctx):
        pnode = ctx.parentCtx.node
        name = ctx.ID().getText()
        ctx.node = col.Get2(pnode, name)
        ctx.node["backend"] = "unknown"

    def exitGet2(self, ctx):
        pass

    def enterGet3(self, ctx):
        pnode = ctx.parentCtx.node
        name = ctx.ID().getText()
        ctx.node = col.Get3(pnode, name)
        ctx.node["backend"] = "unknown"

    def exitGet3(self, ctx):
        pass

    def enterPrefix(self, ctx):
        pre = ctx.PRE().getText()
        parent = ctx.parentCtx
        pnode = parent.node
        if pre == "-":
#              if hasattr(parent, "opr") and \
#                      parent.opr == "+":
#                  ctx.node = pnode
#              else:
                ctx.node = col.Neg(pnode)
        else:
            ctx.node = col.Not(pnode)
        ctx.node["backend"] = "expression"

    def exitPrefix(self, ctx):
        pass

    def enterParen(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Paren(pnode)
        ctx.node["backend"] = "expression"

    def exitParen(self, ctx):
        pass

    def enterIint(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Iint(pnode, ctx.IINT().getText())
        ctx.node["backend"] = "iint"

    def exitIint(self, ctx):
        pass

    def enterString(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.String(pnode, ctx.STRING().getText())
        ctx.node["backend"] = "string"

    def exitString(self, ctx):
        pass

    def enterVar(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Var(pnode, ctx.ID().getText())
        ctx.node.declare()
        ctx.node["backend"] = "unknown"

    def exitVar(self, ctx):
        pass

    def enterInt(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Int(pnode, ctx.INT().getText())
        ctx.node.type("int")
        ctx.node["backend"] = "int"

    def exitInt(self, ctx):
        pass

    def enterCtranspose(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Ctranspose(pnode)
        ctx.node["backend"] = "expression"

    def exitCtranspose(self, ctx):
        pass

    def enterTranspose(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Transpose(pnode)
        ctx.node["backend"] = "expression"

    def exitTranspose(self, ctx):
        pass

    def enterLlist(self, ctx):
        ctx.node = ctx.parentCtx.node

    def exitLlist(self, ctx):
        pass

    def enterListone(self, ctx):
        ctx.node = ctx.parentCtx.node

    def exitListone(self, ctx):
        pass

    def enterListmore(self, ctx):
        ctx.node = ctx.parentCtx.node

    def exitListmore(self, ctx):
        pass

    def enterListall(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.All(pnode)
        ctx.node["backend"] = "expression"

    def exitListall(self, ctx):
        pass

    def enterMatrix(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Matrix(pnode)
        ctx.node["backend"] = "matrix"

    def exitMatrix(self, ctx):
        pass

    def enterVector(self, ctx):
        pnode = ctx.parentCtx.node
        ctx.node = col.Vector(pnode)
        ctx.node["backend"] = "matrix"

    def exitVector(self, ctx):
        pass

    def enterBreak(self, ctx):
        ctx.node = col.Break(ctx.parentCtx.node)
        ctx.node["backend"] = "expression"

    def exitBreak(self, ctx):
        pass
