# Generated from /Users/ttys9/PycharmProjects/pebug/grammar/asm8086.g4 by ANTLR 4.9.2
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .asm8086Parser import asm8086Parser
else:
    from asm8086Parser import asm8086Parser


# This class defines a complete listener for a parse tree produced by asm8086Parser.
class asm8086Listener(ParseTreeListener):

    # Enter a parse tree produced by asm8086Parser#prog.
    def enterProg(self, ctx: asm8086Parser.ProgContext):
        pass

    # Exit a parse tree produced by asm8086Parser#prog.
    def exitProg(self, ctx: asm8086Parser.ProgContext):
        pass

    # Enter a parse tree produced by asm8086Parser#line.
    def enterLine(self, ctx: asm8086Parser.LineContext):
        pass

    # Exit a parse tree produced by asm8086Parser#line.
    def exitLine(self, ctx: asm8086Parser.LineContext):
        pass

    # Enter a parse tree produced by asm8086Parser#instruction.
    def enterInstruction(self, ctx: asm8086Parser.InstructionContext):
        pass

    # Exit a parse tree produced by asm8086Parser#instruction.
    def exitInstruction(self, ctx: asm8086Parser.InstructionContext):
        pass

    # Enter a parse tree produced by asm8086Parser#lbl.
    def enterLbl(self, ctx: asm8086Parser.LblContext):
        pass

    # Exit a parse tree produced by asm8086Parser#lbl.
    def exitLbl(self, ctx: asm8086Parser.LblContext):
        pass

    # Enter a parse tree produced by asm8086Parser#assemblerdirective.
    def enterAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        pass

    # Exit a parse tree produced by asm8086Parser#assemblerdirective.
    def exitAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        pass

    # Enter a parse tree produced by asm8086Parser#rw.
    def enterRw(self, ctx: asm8086Parser.RwContext):
        pass

    # Exit a parse tree produced by asm8086Parser#rw.
    def exitRw(self, ctx: asm8086Parser.RwContext):
        pass

    # Enter a parse tree produced by asm8086Parser#rb.
    def enterRb(self, ctx: asm8086Parser.RbContext):
        pass

    # Exit a parse tree produced by asm8086Parser#rb.
    def exitRb(self, ctx: asm8086Parser.RbContext):
        pass

    # Enter a parse tree produced by asm8086Parser#rs.
    def enterRs(self, ctx: asm8086Parser.RsContext):
        pass

    # Exit a parse tree produced by asm8086Parser#rs.
    def exitRs(self, ctx: asm8086Parser.RsContext):
        pass

    # Enter a parse tree produced by asm8086Parser#cseg.
    def enterCseg(self, ctx: asm8086Parser.CsegContext):
        pass

    # Exit a parse tree produced by asm8086Parser#cseg.
    def exitCseg(self, ctx: asm8086Parser.CsegContext):
        pass

    # Enter a parse tree produced by asm8086Parser#dseg.
    def enterDseg(self, ctx: asm8086Parser.DsegContext):
        pass

    # Exit a parse tree produced by asm8086Parser#dseg.
    def exitDseg(self, ctx: asm8086Parser.DsegContext):
        pass

    # Enter a parse tree produced by asm8086Parser#dw.
    def enterDw(self, ctx: asm8086Parser.DwContext):
        pass

    # Exit a parse tree produced by asm8086Parser#dw.
    def exitDw(self, ctx: asm8086Parser.DwContext):
        pass

    # Enter a parse tree produced by asm8086Parser#db.
    def enterDb(self, ctx: asm8086Parser.DbContext):
        pass

    # Exit a parse tree produced by asm8086Parser#db.
    def exitDb(self, ctx: asm8086Parser.DbContext):
        pass

    # Enter a parse tree produced by asm8086Parser#dd.
    def enterDd(self, ctx: asm8086Parser.DdContext):
        pass

    # Exit a parse tree produced by asm8086Parser#dd.
    def exitDd(self, ctx: asm8086Parser.DdContext):
        pass

    # Enter a parse tree produced by asm8086Parser#equ.
    def enterEqu(self, ctx: asm8086Parser.EquContext):
        pass

    # Exit a parse tree produced by asm8086Parser#equ.
    def exitEqu(self, ctx: asm8086Parser.EquContext):
        pass

    # Enter a parse tree produced by asm8086Parser#if_.
    def enterIf_(self, ctx: asm8086Parser.If_Context):
        pass

    # Exit a parse tree produced by asm8086Parser#if_.
    def exitIf_(self, ctx: asm8086Parser.If_Context):
        pass

    # Enter a parse tree produced by asm8086Parser#assemblerexpression.
    def enterAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        pass

    # Exit a parse tree produced by asm8086Parser#assemblerexpression.
    def exitAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        pass

    # Enter a parse tree produced by asm8086Parser#assemblerlogical.
    def enterAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        pass

    # Exit a parse tree produced by asm8086Parser#assemblerlogical.
    def exitAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        pass

    # Enter a parse tree produced by asm8086Parser#assemblerterm.
    def enterAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        pass

    # Exit a parse tree produced by asm8086Parser#assemblerterm.
    def exitAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        pass

    # Enter a parse tree produced by asm8086Parser#endif_.
    def enterEndif_(self, ctx: asm8086Parser.Endif_Context):
        pass

    # Exit a parse tree produced by asm8086Parser#endif_.
    def exitEndif_(self, ctx: asm8086Parser.Endif_Context):
        pass

    # Enter a parse tree produced by asm8086Parser#end.
    def enterEnd(self, ctx: asm8086Parser.EndContext):
        pass

    # Exit a parse tree produced by asm8086Parser#end.
    def exitEnd(self, ctx: asm8086Parser.EndContext):
        pass

    # Enter a parse tree produced by asm8086Parser#org.
    def enterOrg(self, ctx: asm8086Parser.OrgContext):
        pass

    # Exit a parse tree produced by asm8086Parser#org.
    def exitOrg(self, ctx: asm8086Parser.OrgContext):
        pass

    # Enter a parse tree produced by asm8086Parser#title.
    def enterTitle(self, ctx: asm8086Parser.TitleContext):
        pass

    # Exit a parse tree produced by asm8086Parser#title.
    def exitTitle(self, ctx: asm8086Parser.TitleContext):
        pass

    # Enter a parse tree produced by asm8086Parser#include_.
    def enterInclude_(self, ctx: asm8086Parser.Include_Context):
        pass

    # Exit a parse tree produced by asm8086Parser#include_.
    def exitInclude_(self, ctx: asm8086Parser.Include_Context):
        pass

    # Enter a parse tree produced by asm8086Parser#expressionlist.
    def enterExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        pass

    # Exit a parse tree produced by asm8086Parser#expressionlist.
    def exitExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        pass

    # Enter a parse tree produced by asm8086Parser#label.
    def enterLabel(self, ctx: asm8086Parser.LabelContext):
        pass

    # Exit a parse tree produced by asm8086Parser#label.
    def exitLabel(self, ctx: asm8086Parser.LabelContext):
        pass

    # Enter a parse tree produced by asm8086Parser#expression.
    def enterExpression(self, ctx: asm8086Parser.ExpressionContext):
        pass

    # Exit a parse tree produced by asm8086Parser#expression.
    def exitExpression(self, ctx: asm8086Parser.ExpressionContext):
        pass

    # Enter a parse tree produced by asm8086Parser#multiplyingExpression.
    def enterMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        pass

    # Exit a parse tree produced by asm8086Parser#multiplyingExpression.
    def exitMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        pass

    # Enter a parse tree produced by asm8086Parser#argument.
    def enterArgument(self, ctx: asm8086Parser.ArgumentContext):
        pass

    # Exit a parse tree produced by asm8086Parser#argument.
    def exitArgument(self, ctx: asm8086Parser.ArgumentContext):
        pass

    # Enter a parse tree produced by asm8086Parser#ptr.
    def enterPtr(self, ctx: asm8086Parser.PtrContext):
        pass

    # Exit a parse tree produced by asm8086Parser#ptr.
    def exitPtr(self, ctx: asm8086Parser.PtrContext):
        pass

    # Enter a parse tree produced by asm8086Parser#dollar.
    def enterDollar(self, ctx: asm8086Parser.DollarContext):
        pass

    # Exit a parse tree produced by asm8086Parser#dollar.
    def exitDollar(self, ctx: asm8086Parser.DollarContext):
        pass

    # Enter a parse tree produced by asm8086Parser#register_.
    def enterRegister_(self, ctx: asm8086Parser.Register_Context):
        pass

    # Exit a parse tree produced by asm8086Parser#register_.
    def exitRegister_(self, ctx: asm8086Parser.Register_Context):
        pass

    # Enter a parse tree produced by asm8086Parser#string_.
    def enterString_(self, ctx: asm8086Parser.String_Context):
        pass

    # Exit a parse tree produced by asm8086Parser#string_.
    def exitString_(self, ctx: asm8086Parser.String_Context):
        pass

    # Enter a parse tree produced by asm8086Parser#name.
    def enterName(self, ctx: asm8086Parser.NameContext):
        pass

    # Exit a parse tree produced by asm8086Parser#name.
    def exitName(self, ctx: asm8086Parser.NameContext):
        pass

    # Enter a parse tree produced by asm8086Parser#number.
    def enterNumber(self, ctx: asm8086Parser.NumberContext):
        pass

    # Exit a parse tree produced by asm8086Parser#number.
    def exitNumber(self, ctx: asm8086Parser.NumberContext):
        pass

    # Enter a parse tree produced by asm8086Parser#opcode.
    def enterOpcode(self, ctx: asm8086Parser.OpcodeContext):
        pass

    # Exit a parse tree produced by asm8086Parser#opcode.
    def exitOpcode(self, ctx: asm8086Parser.OpcodeContext):
        pass

    # Enter a parse tree produced by asm8086Parser#rep.
    def enterRep(self, ctx: asm8086Parser.RepContext):
        pass

    # Exit a parse tree produced by asm8086Parser#rep.
    def exitRep(self, ctx: asm8086Parser.RepContext):
        pass

    # Enter a parse tree produced by asm8086Parser#comment.
    def enterComment(self, ctx: asm8086Parser.CommentContext):
        pass

    # Exit a parse tree produced by asm8086Parser#comment.
    def exitComment(self, ctx: asm8086Parser.CommentContext):
        pass


del asm8086Parser
