import board
import busio
import sdcardio
import storage


sd_mnt = '/sd'

def create():
    spi = board.SPI()
    cs = board.A4
    sdcard_blockdevice = sdcardio.SDCard(spi, cs) # this uses SPI, not SDIO
    sd_vfs = storage.VfsFat(sdcard_blockdevice)
    storage.mount(sd_vfs, sd_mnt)
    return sd_mnt

def remove():
    pass

if __name__ == '__main__':
    print(os.listdir(sd_mnt))
    print(os.listdir(sd_mnt + '/DCIM/100MEDIA'))
    with open("/sd/test.txt", "w") as f:
        f.write("Hello world!\r\n")
