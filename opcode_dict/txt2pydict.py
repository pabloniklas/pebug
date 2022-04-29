import re

f = open("opcode.txt")
print("self._opcode = {")

oldcase = ["", "", "", "", ""]

for line in f:
    print("    # LINE ==> " + line[:51])

    opcode = line[:7].strip()
    mnemonic = line[7:16].strip()
    operands = line[16:33].strip()
    flags = line[34:51].strip()

    re.sub("[F,]", "", flags)

    count = 0
    oldcase[0] = "(\\s+)"

    if opcode == "":
        #print("######## LINE EMPTY #######")
        mnemonic = oldcase[2]
        opcode = oldcase[1]
        flags = oldcase[4]
        operands = oldcase[3]

    for oper in operands.split(","):
        if re.match(r"none", oper):
            pass
        elif re.match(r"(mem8|rel8)", oper):
            oldcase[0] = oldcase[0] + "[0-9a-f]{2}"
        elif re.match(r"(mem16|rel16)", oper):
            oldcase[0] = oldcase[0] + "[0-9a-f]{4}"
        elif re.match(r"(mem32|rel32)", oper):
            oldcase[0] = oldcase[0] + "[0-9a-f]{8}"
        elif re.match(r"reg8", oper):
            oldcase[0] = oldcase[0] + "[abcd][hl]"
        elif re.match(r"reg16", oper):
            oldcase[0] = oldcase[0] + "[abcd]x"
        elif re.match(r"reg32", oper):
            oldcase[0] = oldcase[0] + "e[abcd]x"
        elif re.match(r"imm8", oper):
            oldcase[0] = oldcase[0] + "al"
        elif re.match(r"imm16", oper):
            oldcase[0] = oldcase[0] + "ax"

        # Saving the values.
        if opcode != "":
            oldcase[2] = mnemonic
            oldcase[1] = opcode
            oldcase[3] = operands
            oldcase[4] = flags

        # At least one space after the comma. Just my OCD :)
        count += 1

    if count < len(operands):
        oldcase[0] = oldcase[0] + ",(\\s+)"

    # Create the opcodes list
    opcodes = "[ "
    for opc in opcode.split(" "):
        opcodes += f"int(0x{opc}),"

    re.sub(',$', '', opcodes)
    opcodes += " ]"

    print("    r\"^(\\s*)" + mnemonic + oldcase[0] + "\": {")
    print("        \"mnemonic\": \"" + mnemonic + " " + operands + "\",")
    print("        \"opcodes\": " + opcodes + ",")
    print("        \"flags\": \"" + flags + "\"},")

print("}")
f.close()
