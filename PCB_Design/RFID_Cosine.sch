EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L dk_Clock-Timing-Programmable-Timers-and-Oscillators:NE555P U1
U 1 1 61706D0C
P 5050 2950
F 0 "U1" H 5050 3453 60  0000 C CNN
F 1 "NE555P" H 5050 3347 60  0000 C CNN
F 2 "Package_SO:TSSOP-8_4.4x3mm_P0.65mm" H 5250 3150 60  0001 L CNN
F 3 "http://www.ti.com/general/docs/suppproductinfo.tsp?distId=10&gotoUrl=http%3A%2F%2Fwww.ti.com%2Flit%2Fgpn%2Fne555" H 5250 3250 60  0001 L CNN
F 4 "296-1411-5-ND" H 5250 3350 60  0001 L CNN "Digi-Key_PN"
F 5 "NE555P" H 5250 3450 60  0001 L CNN "MPN"
F 6 "Integrated Circuits (ICs)" H 5250 3550 60  0001 L CNN "Category"
F 7 "Clock/Timing - Programmable Timers and Oscillators" H 5250 3650 60  0001 L CNN "Family"
F 8 "http://www.ti.com/general/docs/suppproductinfo.tsp?distId=10&gotoUrl=http%3A%2F%2Fwww.ti.com%2Flit%2Fgpn%2Fne555" H 5250 3750 60  0001 L CNN "DK_Datasheet_Link"
F 9 "/product-detail/en/texas-instruments/NE555P/296-1411-5-ND/277057" H 5250 3850 60  0001 L CNN "DK_Detail_Page"
F 10 "IC OSC SINGLE TIMER 100KHZ 8-DIP" H 5250 3950 60  0001 L CNN "Description"
F 11 "Texas Instruments" H 5250 4050 60  0001 L CNN "Manufacturer"
F 12 "Active" H 5250 4150 60  0001 L CNN "Status"
	1    5050 2950
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x04_Male J1
U 1 1 61708420
P 4000 2950
F 0 "J1" H 4108 3231 50  0000 C CNN
F 1 "Conn_01x04_Male" H 4108 3140 50  0000 C CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical" H 4000 2950 50  0001 C CNN
F 3 "~" H 4000 2950 50  0001 C CNN
	1    4000 2950
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x04_Male J2
U 1 1 61708F7B
P 6275 3075
F 0 "J2" H 6247 2957 50  0000 R CNN
F 1 "Conn_01x04_Male" H 6247 3048 50  0000 R CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical" H 6275 3075 50  0001 C CNN
F 3 "~" H 6275 3075 50  0001 C CNN
	1    6275 3075
	-1   0    0    1   
$EndComp
Wire Wire Line
	5050 3350 4325 3350
Wire Wire Line
	4325 3350 4325 2850
Wire Wire Line
	4325 2850 4200 2850
Wire Wire Line
	4550 3050 4275 3050
Wire Wire Line
	4275 3050 4275 2950
Wire Wire Line
	4275 2950 4200 2950
Wire Wire Line
	5550 3050 5550 3375
Wire Wire Line
	5550 3375 4250 3375
Wire Wire Line
	4250 3375 4250 3050
Wire Wire Line
	4250 3050 4200 3050
Wire Wire Line
	4550 2850 4450 2850
Wire Wire Line
	4450 2850 4450 3150
Wire Wire Line
	4450 3150 4200 3150
Wire Wire Line
	5050 2650 6075 2650
Wire Wire Line
	6075 2650 6075 2875
Wire Wire Line
	5550 2950 6075 2950
Wire Wire Line
	6075 2950 6075 2975
Wire Wire Line
	5975 2325 5975 3075
Wire Wire Line
	5975 3075 6075 3075
Wire Wire Line
	4550 3150 4550 3475
Wire Wire Line
	4550 3475 6075 3475
Wire Wire Line
	6075 3475 6075 3175
Wire Wire Line
	4550 2950 4500 2950
Wire Wire Line
	4500 2950 4500 2325
Wire Wire Line
	4500 2325 5975 2325
$EndSCHEMATC
