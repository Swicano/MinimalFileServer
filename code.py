# Write your code here :-)
import asyncio as aio
import myserve
import microcontroller

async def printsmth(poll_time_s):
    while True:
        await aio.sleep(poll_time_s)
        print(f"the poll time is {poll_time_s}")


async def writesmth_tofile(poll_time_s):
    while True:
        # open file for append
        await aio.sleep(poll_time_s)
        with open("/sd/temperature.txt", "a") as f:
            #led.value = True # turn on LED to indicate we're writing to the file
            t = microcontroller.cpu.temperature
            print("Temperature = %0.1f" % t)
            f.write("%0.1f\n" % t)
            #led.value = False # turn off LED to indicate we're done
            # file is saved


async def main():
    srv = myserve.connect_build_srv()
    serve_task = aio.create_task(myserve.run_polling(srv,10.0))
    prnt_task = aio.create_task(printsmth(10))
    prnt_task = aio.create_task(writesmth_tofile(20))

    await aio.gather(serve_task,prnt_task)

aio.run(main())


#loop = aio.get_event_loop()
#srv = myserve.connect_build_srv()
#try:
#    aio.ensure_future(printsmth(1))
#    aio.ensure_future(myserve.run_polling(srv,0.1))
#    loop.run_forever()
#except KeyboardInterrupt:
#    pass
#finally:
#    print("Closing loop")
#    loop.close()
