#############################################################################
##
##  KLA client error log parsing patterns
##
## Copyright (C) 2015 Kollective Technology.  All rights reserved.
##
#############################################################################

__author__ = 'john'

# Th-0                 [Nov 24 19:34:09] DMGR     IPInterface::Init() before
# [54fc]IP config      [Nov 24 19:34:09] IPCONFIG GetCOMInterfaces ENTRY || IPCONFIG IP network configuration changed!!
# [54fc]IP config      [Nov 24 19:34:09] IPCONFIG Adapter name: c02d478b-10f3-4191-9aea-b27e8f69c9d1
# [54fc]IP config      [Nov 24 19:34:09] IPCONFIG Adapter description: [Microsoft Virtual WiFi Miniport Adapter]
# [54fc]IP config      [Nov 24 19:34:09] IPCONFIG Chars: NCF_VIRTUAL, adding...

patternDef = {
    "prefix": r'^(\[?(?P<threadID>([a-f0-9]+)|(Th-0))\]?)*(?P<threadName>[a-zA-Z ]+)\[(?P<timestamp>\w+ \d+ \d+:\d+:\d+\])\s*',
    "tasks": {
        "network.IPConfig": {
            "prefix": r'(?P<module>IPCONFIG) ',
            "start": [ r'GetCOMInterfaces ENTRY', ],
            "patterns": [ r'CheckForBroadband: Found an interface with speed\((?P<foundBroadband>\d+)\) greater than 64K',
                          r'ZIPConfig::UpdateRouting Default Gateway  index=(?P<defaultGatewayIndex>\d+), subnet gateway=(?P<subnetGateway>[0-9\.])', ],
            "subtasks": {
                "adapters": {
                    "prefix": r'(?P<module>IPCONFIG) ',
                    "start": [ r'Adapter name: (?P<name>.*)', ],
                    "patterns": [ r'Adapter description: (?P<description>.*)',],
                    "end":  [
                        r'Chars: (?P<type>\w+), adding...',
                        r'Device has invalid status\((?P<invalidStatus>[^)]*)\), (?P<ignored>ignoring)...',
                        r'GetDeviceStatus\(\) failed, (?P<ignored>ignoring)..., (?P<GetDeviceStatus_failed>.*)',
                    ],
                    "indexFields": ['name']
                },
                "interfaces": {
                    "prefix": r'(?P<module>IPCONFIG) ',
                    "start": [ r'Adding interface: type=(?P<type>\d+), description=(?P<description>.*\]), MTU=(?P<mtu>\d+), Speed=(?P<speed>\d+), Index=(?P<index>\d+), IsRunning=(?P<isRunning>\d+)', ],
                    "indexFields": ["index", ]
                }
            },
            "end":  [ r'CheckForBroadband:.*' ],
        },
        "peer": {
            "prefix": r'(?P<module>PEER)\s+',
            "patterns": [ r'ZPeerInventory:init self nodeid=(?P<nodeID>.*)',
                          r'ZPeerKDPReceiver::ZPeerKDPReceiver: KDP using port (?P<kdpPort>\d+)', ],
        }
    }
}



# Th-0                 [Nov 24 19:34:10] PEER     ZPeerInventory:init self nodeid=pDPTu3/AT2k1pzhfLPp6TRehJCCglVynBl0Dc0IS1ER99HzKZeOjai080X8wRFSX9TbWDFGxgZrXojM/lYX5K5i3lv8kgOnD3x9DmUIOtJaOdBQ8NBojfbGvabwC6hEEOo6ETXK0lUcucgO0xo/ChUxysO/0jkXGIC86PYUPp62R
# Th-0                 [Nov 24 19:34:10] PEER     Priority threshold 0 is -1.79769313486e+308
# Th-0                 [Nov 24 19:34:10] PEER     Priority threshold 1 is 0
# Th-0                 [Nov 24 19:34:10] PEER     Addr and Grid Policy: noderef=[address=172.16.77.74 port=1947 version=v1.33 ]
# Th-0                 [Nov 24 19:34:10] DMSMGR   ZConnectionFailover::resetFailback
# Th-0                 [Nov 24 19:34:10] PEER     setting signer to pDPTu3/AT2k1pzhfLPp6TRehJCCglVynBl0Dc0IS1ER99HzKZeOjai080X8wRFSX9TbWDFGxgZrXojM/lYX5K5i3lv8kgOnD3x9DmUIOtJaOdBQ8NBojfbGvabwC6hEEOo6ETXK0lUcucgO0xo/ChUxysO/0jkXGIC86PYUPp62R
# Th-0                 [Nov 24 19:34:10] PEER     ZPeerKDPReceiver::ZPeerKDPReceiver: KDP using port 1947
