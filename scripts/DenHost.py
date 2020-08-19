import argparse
import asyncio
import logging
import os

from aioconsole import ainput

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
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
    await asyncio.sleep(5)
    # Exit pairing controllers
    await asyncio.sleep(5)
    await button_push(controller_state, 'a')
    await asyncio.sleep(5)
    await button_push(controller_state, 'down')
    await button_push(controller_state, 'down')
    await button_push(controller_state, 'down')
    await button_push(controller_state, 'a')
    await asyncio.sleep(5)
    #     At the home screen
    await button_push(controller_state, 'up')
    await button_push(controller_state, 'left')
    await button_push(controller_state, 'left')

async def openPkm(controller_state):
    #open
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    await asyncio.sleep(2)
    await button_push(controller_state, 'a')
    await asyncio.sleep(2)
    #sleep to get into the game


async def setLinkCode(controller_state):
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
    #open ycom
    await button_push(controller_state, 'y')
    await button_push(controller_state, 'plus')
    #sleep to go online
    await asyncio.sleep(8)
    await button_push(controller_state, 'b')
    await button_push(controller_state, 'b')

    #open den
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    await button_push(controller_state, 'a')
    #TODO: frame skip 3 days
    await setLinkCode()
    await button_push(controller_state, 'a') #start den
    #small sleep 1s?
    await asyncio.sleep(1)
    await button_push(controller_state, 'up') #start den
    await button_push(controller_state, 'a') #start den
    #TODO: wait until the 2m mark (wait 60s)
    await asyncio.sleep(60)
    await button_push(controller_state, 'a') #start den
    await button_push(controller_state, 'a') #start den
    #sleep 15s
    await asyncio.sleep(15)

    await button_push(controller_state, 'home') #exit raid and close pkm
    await button_push(controller_state, 'x')
    await button_push(controller_state, 'a')





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
