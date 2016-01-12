#############################################################################
##
##  KLA client error log parsing patterns
##
## Copyright (C) 2015 Kollective Technology.  All rights reserved.
##
#############################################################################

__author__ = 'john'

patternDef = {
    "prefix": r'^(\[?(?P<threadID>([a-f0-9]+)|(Th-0))\]?)*(?P<threadName>[a-zA-Z0-9 ]+)\[(?P<timestamp>\w+ \d+ \d+:\d+:\d+)\]\s*',
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
                },
                "listeners": {
                    "prefix": r'(?P<module>PEER     )',
                    "start": [ r'(?P<name>KHTTPServer): (?P<address>.*)',
                                  r'(?P<name>ZPeerListener)::start listening on port (?P<port>.*)',
                                  r'(?P<name>RTMPServer) listening on (?P<address>.*)'],
                    "indexFields": ["name"]
                }
            }
        },
        "peer": {
            "prefix": r'(?P<module>PEER)\s+',
            "patterns": [ r'ZPeerInventory:init self nodeid=(?P<nodeID>.*)',
                          r'ZPeerKDPReceiver::ZPeerKDPReceiver: KDP using port (?P<kdpPort>\d+)',
                          r'Addr and Grid Policy: noderef=\[(?P<noderef>.*)\]'
                          ],
        },
        "download": {
            "prefix": r'(?P<module>DMGR     |PEER     )',
            "start": [ r'selecting moid for download: (?P<moid>[0-9a-f\-]+).*', ],
            "subtasks": {
                "progress": {
                    "prefix": r'(?P<module>PEER     )',
                    "start": [ r'ZPeerProtoLoaderZBBP::progress started moid=(?P<moid>[0-9a-f\-]+) nodeid=(?P<nodeID>[0-9a-zA-Z]+) \((?P<bytes>\d+) bytes\)', ],
                }
            },
            # "patterns": [
            #     r'ZPeer::stream\((?P<moid>[0-9a-f\-]+)\) ready to stream',
            #     r'ZPeerProtoLoaderZBBP::progress started moid=(?P<moid>[0-9a-f\-]+) nodeid=(?P<nodeID>[0-9a-zA-Z]+) \((?P<bytes>\d+) bytes\)',
            # ],
            "end":  [ r'ZPeer:endLoad for moid=(?P<moid>[0-9a-f\-]+) reports:(?P<endLoadReport>\w+).*' ],
        }
    }
}

# PEER     KHTTPServer: http://127.0.0.1:31013
# RTMPServer listening on rtmp://127.0.0.1:31014
#[57b4]ZUserDownload  [Nov 24 19:43:41] DMGR     selecting moid for download: 6174a797-ba2c-291f-bfde-dc2ed217cfc1
#Th-0                 [Nov 24 20:53:48] PEER     ZPeer:endLoad for moid=6174a797-ba2c-291f-bfde-dc2ed217cfc1 reports:ZPEER_ABANDONED
#[57b4]ZUserDownload  [Nov 24 19:43:42] PEER     ZPeer::stream(6174a797-ba2c-291f-bfde-dc2ed217cfc1) ready to stream
#[24a0]L1             [Nov 24 19:45:04] PEER     ZPeerProtoLoaderZBBP::progress started moid=6174a797-ba2 nodeid=g5hxp7CNcvON (4073601 bytes)
