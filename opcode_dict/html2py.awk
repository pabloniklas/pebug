{
    gsub("[F,]", "", $4)

    split($3, operands, ",")

    syntax = "(\\s+)"
    count = 0
    detected = FALSE
    for (oper in operands) {
        switch (operands[oper]) {
            case /(mem8|rel8)/:
                syntax = syntax "[0-9a-f]{2}"
                detected = TRUE
                break
            case /(mem16|rel16)/:
                syntax = syntax "[0-9a-f]{4}"
                detected = TRUE
                break
            case "reg8":
                syntax = syntax "[abcd][hl]"
                detected = TRUE
                break
            case "reg16":
                syntax = syntax "[abcd]x"
                detected = TRUE
                break
            case "imm8":
                syntax = syntax "al"
                detected = TRUE
                break
            case "imm16":
                syntax = syntax "ax"
                detected = TRUE
                break

        }
        if (detected == TRUE) {
            syntax = syntax "(\\s*)"
        }
        count++
        if (count < length(operands)) {
            syntax = syntax ",(\\s+)"
        }
    }

    print "r\"^(\\s*)" $2 syntax "\": {"
    print "    \"mnemonic\": \"" $2 " " $3 "\","
    print "    \"opcode\": int(0x" $1 "),"
    print "    \"flags\": \"" $4 "\"},"
}
