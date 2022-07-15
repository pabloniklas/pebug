# Generated from /Users/ttys9/PycharmProjects/pebug/grammar/asm8086.g4 by ANTLR 4.9.2
from antlr4 import *

if __name__ is not None and "." in __name__:
    from modules.asm8086Parser import asm8086Parser
else:
    from modules.asm8086Parser import asm8086Parser


# This class defines a complete generic visitor for a parse tree produced by asm8086Parser.

class asm8086Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by asm8086Parser#prog.
    def visitProg(self, ctx: asm8086Parser.ProgContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#line.
    def visitLine(self, ctx: asm8086Parser.LineContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#instruction.
    def visitInstruction(self, ctx: asm8086Parser.InstructionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#lbl.
    def visitLbl(self, ctx: asm8086Parser.LblContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#assemblerdirective.
    def visitAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#rw.
    def visitRw(self, ctx: asm8086Parser.RwContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#rb.
    def visitRb(self, ctx: asm8086Parser.RbContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#rs.
    def visitRs(self, ctx: asm8086Parser.RsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#cseg.
    def visitCseg(self, ctx: asm8086Parser.CsegContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#dseg.
    def visitDseg(self, ctx: asm8086Parser.DsegContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#dw.
    def visitDw(self, ctx: asm8086Parser.DwContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#db.
    def visitDb(self, ctx: asm8086Parser.DbContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#dd.
    def visitDd(self, ctx: asm8086Parser.DdContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#equ.
    def visitEqu(self, ctx: asm8086Parser.EquContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#if_.
    def visitIf_(self, ctx: asm8086Parser.If_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#assemblerexpression.
    def visitAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#assemblerlogical.
    def visitAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#assemblerterm.
    def visitAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#endif_.
    def visitEndif_(self, ctx: asm8086Parser.Endif_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#end.
    def visitEnd(self, ctx: asm8086Parser.EndContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#org.
    def visitOrg(self, ctx: asm8086Parser.OrgContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#title.
    def visitTitle(self, ctx: asm8086Parser.TitleContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#include_.
    def visitInclude_(self, ctx: asm8086Parser.Include_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#expressionlist.
    def visitExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#label.
    def visitLabel(self, ctx: asm8086Parser.LabelContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#expression.
    def visitExpression(self, ctx: asm8086Parser.ExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#multiplyingExpression.
    def visitMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#argument.
    def visitArgument(self, ctx: asm8086Parser.ArgumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#ptr.
    def visitPtr(self, ctx: asm8086Parser.PtrContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#dollar.
    def visitDollar(self, ctx: asm8086Parser.DollarContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#register_.
    def visitRegister_(self, ctx: asm8086Parser.Register_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#string_.
    def visitString_(self, ctx: asm8086Parser.String_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#name.
    def visitName(self, ctx: asm8086Parser.NameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#number.
    def visitNumber(self, ctx: asm8086Parser.NumberContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#opcode.
    def visitOpcode(self, ctx: asm8086Parser.OpcodeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#rep.
    def visitRep(self, ctx: asm8086Parser.RepContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by asm8086Parser#comment.
    def visitComment(self, ctx: asm8086Parser.CommentContext):
        return self.visitChildren(ctx)


del asm8086Parser
