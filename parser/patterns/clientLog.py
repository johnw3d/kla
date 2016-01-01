#############################################################################
##
##  KLA client error log parsing patterns
##
## Copyright (C) 2015 Kollective Technology.  All rights reserved.
##
#############################################################################

__author__ = 'john'

patternDef = {
    "prefix": r'^(\[?(?P<threadID>([a-f0-9]+)|(Th-0))\]?)*(?P<threadName>[a-zA-Z ]+)\[(?P<timestamp>\w+ \d+ \d+:\d+:\d+)\]\s*',
    "tasks": {
        "network": {
            "subtasks": {
                "IPConfig": {
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
                            "indexFields": ['description']
                        },
                        "interfaces": {
                            "prefix": r'(?P<module>IPCONFIG) ',
                            "start": [ r'Adding interface: type=(?P<type>\d+), description=(?P<description>.*\]), MTU=(?P<mtu>\d+), Speed=(?P<speed>\d+), Index=(?P<index>\d+), IsRunning=(?P<isRunning>\d+)', ],
                            "indexFields": ["index", ]
                        }
                    },
                    "end":  [ r'CheckForBroadband:.*' ],
                },
                "dirsrvTrace": {
                    "prefixMatch": { "threadName": "ZPeerDirSrvTra", },
                    "prefix": r'(?P<module>PEER_DST |ZPING    )',
                    "start": [ r'ZPeerDirsrvTracer::run - start dirsrv traceRoute', ],
                    "subtasks": {
                        "pings": {
                            "prefixMatch": { "threadName": "ZPeerDirSrvTra", },
                            "prefix": r'(?P<module>PEER_DST |ZPING    )',
                            "start": [ r'ZPing ICMP addr=(?P<addr>[0-9\.]+), maxHops=(?P<maxHops>\d+), replyfrom:(?P<replyfrom>[0-9\.]+), rtt=(?P<rtt>[^,]+), status=(?P<status>.*)',],
                            "indexFields": ["replyfrom"]
                        }
                    },
                    "end":  [ r'ZPeerDirsrvTracer::run dirsrv trace done' ],
                }
                # "dirsrvTrace.pings": {
                #     "threadName": "ZPeerDirSrvTra",
                #     "prefix": r'(?P<module>PEER_DST |ZPING    )',
                #     "start": [ r'ZPeerDirsrvTracer::run - start dirsrv traceRoute', ],
                #     "patterns": [ r'ZPing ICMP addr=(?P<addr>[0-9\.]+), maxHops=(?P<maxHops>\d+), replyfrom:(?P<replyfrom>[0-9\.]+), rtt=(?P<rtt>[^,]+), status=(?P<status>.*)',],
                #     "indexFields": ["replyfrom"],
                #     "end":  [ r'ZPeerDirsrvTracer::run dirsrv trace done' ],
                # }
            }
        },
        "peer": {
            "prefix": r'(?P<module>PEER)\s+',
            "patterns": [ r'ZPeerInventory:init self nodeid=(?P<nodeID>.*)',
                          r'ZPeerKDPReceiver::ZPeerKDPReceiver: KDP using port (?P<kdpPort>\d+)',
                          r'Addr and Grid Policy: noderef=\[(?P<noderef>.*)\]'
                          ],
        }
    }
}

