import re

f = open("opcode.txt")
print("self._opcode = {")
line32 = False

oldcase = ["", "", "", "", ""]

for line in f:
    print("    # SOURCE LINE ==> " + line[:51])

    # Only 16 bits (or less =)
    if re.search(r'(32)|(E[ABCD]X)|E(SBI)P',
                 line.strip(), re.MULTILINE) is None and line[16:33].strip() != "":

        line32 = False
        opcode = line[:7].strip()
        mnemonic = line[7:16].strip()
        operands = line[16:33].strip()
        flags = line[34:51].strip()

        re.sub("[F,]", "", flags)

        count = 0
        oldcase[0] = "(\\s+)"

        if opcode == "" and mnemonic != oldcase[2]:  # Empty line, recover the values of previusly filled line
            mnemonic = oldcase[2]
            opcode = oldcase[1]
            flags = oldcase[4]
            operands = oldcase[3]

        for oper in operands.split(","):
            if re.match(r"none", oper):
                pass
            elif re.match(r"(mem8|rel8)", oper):
                oldcase[0] += "[0-9a-f]{2}"
            elif re.match(r"(mem16|rel16)", oper):
                oldcase[0] += "[0-9a-f]{4}"
            elif re.match(r"reg8", oper):
                oldcase[0] += "[abcd][hl]"
            elif re.match(r"reg16", oper):
                oldcase[0] += "[abcd]x"
            elif re.match(r"imm8", oper):
                oldcase[0] += "al"
            elif re.match(r"imm16", oper):
                oldcase[0] += "ax"
            elif re.match(r"\b([CDEFGS]S)\b|\b([SD]I)\b|\b([ABCDE]X)\b|\b([ABCD][HL])\b|\b([SBI]P)\b",
                          oper, re.IGNORECASE):
                oldcase[0] += f"{oper}"

            # Saving the values.
            if opcode != "":
                oldcase[1] = opcode
                oldcase[2] = mnemonic
                oldcase[3] = operands
                oldcase[4] = flags

            # At least one space after the comma. Just my OCD :)
            count += 1

            if count < len(operands) - 2:
                oldcase[0] = oldcase[0] + ",(\\s+)"
            else:
                oldcase[0] = oldcase[0] + "(\\s+)"

        # Create the opcodes list
        opcodes_list_count = 0
        opcodes = "[ "
        for opc in opcode.split(" "):
            opcodes_list_count += 1
            if opcodes_list_count < len(opcode.split(" ")):
                opcodes += f"int(0x{opc}),"
            else:
                opcodes += f"int(0x{opc})"

        opcodes += " ]"

        if line32 is False:
            print("    r\"^(\\s*)" + mnemonic + oldcase[0] + "\": {")
            print("        \"mnemonic\": \"" + mnemonic + " " + operands + "\",")
            print("        \"opcodes\": " + opcodes + ",")
            print("        \"flags\": \"" + flags + "\"},")
    else:
        line32 = True

print("}")
f.close()
