#!/usr/bin/python

"""
$Log: asmconsts.py,v $
Revision 1.4  2007/09/07 15:23:56  joxean
Correct support for sparc.

Revision 1.3  2007/09/06 20:40:37  joxean
Initial support for sparc processors.

Revision 1.2  2007/09/05 16:11:53  joxean
Constants for AVR binaries

"""

AVAILABLE_CPUS = ["x86", "avr", "sparc", "unknown"]

IGNORE_INSTRUCTIONS = {}
IGNORE_INSTRUCTIONS["x86"] = ["REMOVETOIGNOREpush%ebp", "REMOVETOIGNOREmov%esp,%ebp", 
                                                        "REMOVETOIGNOREleave", "REMOVETOIGNOREret", "nop", "hlt"]

IGNORE_INSTRUCTIONS_DES = {}
IGNORE_INSTRUCTIONS_DES["x86"] = ["push%ebp", "mov%esp,%ebp", "pop%ebp", "leave", "nop", "hlt"]

IGNORE_INSTRUCTIONS["avr"] = ["REMOVETOIGNOREpushr28", "REMOVETOIGNOREpushr29", "REMOVETOIGNOREret", "nop"]
IGNORE_INSTRUCTIONS["sparc"] = ["REMOVETOIGNOREstwrp,-14(sp)", "REMOVETOIGNOREcopyr26,r23", "nop"]
IGNORE_INSTRUCTIONS["mips"] = ["nop"]
IGNORE_INSTRUCTIONS["unknown"] = "ret"

# Mainly, gcc generated functions
IGNORE_FUNCTIONS = [ # The most common for x86
                                       "call_gmon_start", "_start", "__i686.get_pc_thunk.bx", 
                                       "__do_global_dtors_aux", "frame_dummy", "__libc_csu_init",
                                       "__libc_csu_fini", "__do_global_ctors_aux", "__do_global_dtors_aux",
                                       "__do_register_frame", "__do_deregister_frame",
                                       "__libc_do_global_destruction", "__icrt_terminate", "__icrt_init", 
                                       "__x86_jump_to_context",
                                       # The most common for avr
                                       "__bad_interrupt", ".do_clear_bss_start", ".do_clear_bss_loop",
                                       "__do_clear_bss", ".do_copy_data_start", ".do_copy_data_loop",
                                       "__do_copy_data", "__ctors_end", "__vectors", "__epilogue_restores__",
                                       "__prologue_saves__", "__udivmodsi4_ep", "__udivmodsi4_loop",
                                       "__udivmodsi4", "__mulhi3_exit", "__mulhi3_skip1", "__mulhi3_loop",
                                       "__mulhi3", ".memset_start", ".memset_loop", ".strnlen_loop", 
                                       ".strlen_P_loop", ".strcpy_loop", 
                                       # For Sparc
                                       "__gmon_start__", "alarm_handler"
                                       ]

INTERESTING_INSTRUCTIONS = {}
INTERESTING_INSTRUCTIONS["x86"] = ["call*%", "jmp*%"]
INTERESTING_INSTRUCTIONS["avr"] = []
INTERESTING_INSTRUCTIONS["sparc"] = []
INTERESTING_INSTRUCTIONS["mips"] = []
INTERESTING_INSTRUCTIONS["unknown"] = ["call", "jmp"]

WARNING_CALLS = ["strcpy", "strncpy", "strcat", "strncat", "printf", "puts", "gets", "scanf", "wcscpy", "tcscpy", "mbscpy",
                                    "wcscat", "tcscat", "mbscat","wcsncat", "tcsncat", "mbsncat", "strccpy", "strcadd", "getts", "syslog",
                                    "strlen", "wcslen", "tcslen", "mbslen", "MultiByteToWideChar", "strecpy", "streadd", "strtrns",
                                    "chroot", "getenv", "SetSecurityDescriptorDacl", "recv"]

DOUBLE_CHECK_CALLS = ["malloc", "free"]
USER_CONTROLLED_DATA = {}
USER_CONTROLLED_DATA["x86"] = ["push%"]
USER_CONTROLLED_DATA["avr"] = ["pushr"]
USER_CONTROLLED_DATA["sparc"] = ["copy"]
USER_CONTROLLED_DATA["unknown"] = []

FUNCTION_START = {}
FUNCTION_START["x86"] = ["push%ebp", "mov%esp,%ebp"]
FUNCTION_START["avr"] = ["pushr28", "pushr29"]
FUNCTION_START["sparc"] = ["stwrp,-14(sp)", "copyr26,r23"]
FUNCTION_START["mips"] = ["iduknow1", "iduknow2"]
FUNCTION_START["unknown"] = ["nonexistent1", "nonexistent2"]

FUNCTION_END = {}
FUNCTION_END["x86"] = ["leave", "ret"]
FUNCTION_END["avr"] = ["popr29", "popr28", "ret"]
FUNCTION_END["sparc"] = []
FUNCTION_END["mips"] = []
FUNCTION_END["unknown"] = []

# "ret" is not a JUMP instruction but, well, it should be considered
JUMP_INSTRUCTIONS = {}
JUMP_INSTRUCTIONS["x86"] = ["call", "je", "jle", "jmp", "jnz", "jn", "jz", "jo", "jno", "js", "jns", "je", "jz", "jne", "jnz", 
                                                "jb", "jnae", "jc", "jnb", "jae", "jnc", "jbe", "jna", "ja", "jnbe", "jl", "jnge", "jnl", "jng", 
                                                "jg", "jnle", "jp", "jpe", "jnp", "jpo", "jcxz", "jecxz", "jg", "jge", "jle", "ret"]
JUMP_INSTRUCTIONS["avr"] = ["call", "icall", "br", "ret", "brne", "rcall", "brcc", "brcs", "breq", "brge", "brlt", "brne", "rjmp",
                                                "ijmp", "ret"]
JUMP_INSTRUCTIONS["sparc"] = ["j", "jr", "jal", "beq", "bne", "bltz", "bgez", "slt", "slti", "sltiu", "b,l", "b", "cmpib", "cmpb",
                                                    "bb", "movb", "addib", "movib", "addb", "cmib", "ret"]
JUMP_INSTRUCTIONS["mips"] = ["beq", "beqz", "beqzl", "bl", "ble", "blez", "bg", "bge", "bgez", "blt", "bltz", "bn", "bne", "bnez",
                                                       "j", "ja", "jal", "jalr", "jl", "jlr", "jr"]
JUMP_INSTRUCTIONS["unknown"] = []

for cpu in JUMP_INSTRUCTIONS:
    JUMP_INSTRUCTIONS["unknown"] += JUMP_INSTRUCTIONS[cpu] # That is a fucking hack!

CURRENT_CPU = "x86" # By default

