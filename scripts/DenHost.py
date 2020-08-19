import asyncio
import logging
import os


from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import button_push
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

logger = logging.getLogger(__name__)

async def _main():
    spi_flash = FlashMemory()

    # Get controller name to emulate from arguments
    controller = Controller.from_arg("PRO_CONTROLLER")

    with utils.get_output(path=None, default=None) as capture_file:
        # prepare the the emulated controller
        factory = controller_protocol_factory(controller, spi_flash=spi_flash)
        ctl_psm, itr_psm = 17, 19
        transport, protocol = await create_hid_server(factory, reconnect_bt_addr=None,
                                                      ctl_psm=ctl_psm,
                                                      itr_psm=itr_psm, capture_file=capture_file,
                                                      device_id=None)

        controller_state = protocol.get_controller_state()

        # Create command line interface and add some extra commands
        try:
            loop = asyncio.get_event_loop()
            await exitPeering(controller_state)
            loop.run_until_complete(
                await autoHost(controller_state)
            )
        finally:
            logger.info('Stopping communication...')
            await transport.close()


async def autoHost(controller_state):
    await openPkm(controller_state)
    await startDen(controller_state)


async def exitPeering(controller_state):
    logger.info("Waiting for peering")
    await asyncio.sleep(5)
    # Exit pairing controllers
    logger.info("Exiting to home menu")
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)
    #     At the home screen

async def openPkm(controller_state):
    logger.info("Opening pokemon")
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a', sec=1)

    logger.info("Selecting user")
    await button_push(controller_state, 'a', sec=1)

    logger.info("Waiting for pokemon to start")
    await asyncio.sleep(15)
    await button_push(controller_state, 'a', sec=1)
    logger.info("Waiting to get into the game")
    await asyncio.sleep(8)
    #sleep to get into the game


async def setLinkCode(controller_state):
    logger.info("Setting linkcode 1111 2114")
    await button_push(controller_state, 'plus')
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'right')  # 2
    await button_push(controller_state, 'a')  # 2
    await button_push(controller_state, 'left')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'down')  # 1
    await button_push(controller_state, 'a')  # 1
    await button_push(controller_state, 'plus')  # 1
    #tiny sleep here
    await asyncio.sleep(1)
    await button_push(controller_state, 'a')  # 1


async def startDen(controller_state):
    logger.info("Connecting to internet")
    #open ycom
    await button_push(controller_state, 'y')
    await button_push(controller_state, 'plus')
    #sleep to go online
    await asyncio.sleep(8)
    await button_push(controller_state, 'b')
    await button_push(controller_state, 'b')

    logger.info("Open den")
    #open den
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    #TODO: frame skip 3 days
    logger.info("Start den")
    await setLinkCode(controller_state)
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    logger.info("Ready up")

    await button_push(controller_state, 'up')
    await button_push(controller_state, 'a') #start den
    logger.info("Wait till 2mins ish left")
    await asyncio.sleep(60)
    logger.info("actually start")
    await button_push(controller_state, 'a') #start den
    await button_push(controller_state, 'a') #start den
    #sleep 15s
    logger.info("Make sure we are in the raid")
    await asyncio.sleep(15)

    logger.info("quit and close pokemon")
    await button_push(controller_state, 'home') #exit raid and close pkm
    await button_push(controller_state, 'x')
    await button_push(controller_state, 'a')
    await asyncio.sleep(10)





if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    #log.configure(console_level=logging.ERROR)
    log.configure()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _main()
    )
