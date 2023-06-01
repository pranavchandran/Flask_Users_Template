    def ValidationByComponent(self, config, PendingAlertsData, MulData, alertValidationFlag):

        for index, eachAlert in PendingAlertsData.iterrows():

            EquipmentAlarmID, TagsList = eachAlert['EquipmentAlarmID'], eachAlert['Tags']
            # AlarmName, SiteName, OSMName = eachAlert['AlarmName'], eachAlert['Site'], eachAlert['OSM']
            # EquipmentSrNo, Status, Model = eachAlert['EquipmentSerNum'], eachAlert['Status'], eachAlert['Model']

            try:
                AppliestoAllUnits = self.GetSensorValue(EquipmentAlarmID)
            except Exception as ex:
                AppliestoAllUnits = 0
            logging.info("EquipmentAlarmID :" + str(EquipmentAlarmID))

            if len(PendingAlertsData) > 40:
                break
            elif len(PendingAlertsData) > 0:
                OSMIPAddress, RouterIP, iLO_GE_IP, HyperVisor_IP = "", "", "", ""
                OSMIPData = self.getOSMIPAddress()
            else:
                OSMIPData = ''
            # for index, eachAlert in PendingAlertsData.iterrows():
            OSMIPAddress, RouterIP, iLO_GE_IP, HyperVisor_IP = '', '', '', ''
            AlertNotes, PingStatusFlag = '', 0
            # AlertStatus = 'PENDING-READY'
            AlertStatus = ''
            FinalComments = ''
            OSMIP_PingStatus, RouterIP_PingStatus, iLO_GE_IP_PingStatus, HyperVisor_IP_PingStatus = '', '', '', ''
            OSMIPMismatch = 0
            EquipmentAlarmID, AlarmName = eachAlert['EquipmentAlarmID'], eachAlert['AlarmName']
            # TODO change OSMName to OSM impacting here
            OSMIPAddress, SiteName, OSMName = eachAlert['OSMIP'], eachAlert['Site'], eachAlert['OSM']
            EquipmentSrNo, Status, Model = eachAlert['EquipmentSerNum'], eachAlert['Status'], eachAlert['Model']
            logging.info("##########################" + str(EquipmentAlarmID) + "##########################")
            # TODO for testing i inserted QA but there is it wont match with identity_column
            # TODO After test Need to restore back these lines
            SolarWindFlag, AlertsSensorValueData = self.GetSensorValue(EquipmentAlarmID)
            RouterIP = self.getRouterDetails(SiteName)
            iLO_GE_IP, HyperVisor_IP = self.getiLO_Hypervisor(OSMName)
            logging.info("OSM IP : " + str(OSMIPAddress))

            MULOSMIP = OSMIPData[OSMIPData['OSMName'].str.contains(OSMName)]['IPAddress'].tolist()

            if len(MULOSMIP) > 0:
                if MULOSMIP[0].upper().strip() != OSMIPAddress.upper().strip():
                    OSMIPMismatch = 1
                OSMIPAddress = MULOSMIP[0].upper().strip()
            AlarmName = 'APM-THERMAL OSM ALERTS'
            IDSMapping = self.GetIDSMapping(AlarmName)
            ExceptionsCheckFlag, ExceptionCategory = self.CheckExceptions(OSMName)
            DuplicateCheckFlag, CaseDetails, Status = self.CheckMNDDuplicateCases(OSMName, IDSMapping)

            if (ExceptionsCheckFlag == 1):
                AlertNotes = 'Exception Exist : ' + (ExceptionCategory) + "\n\n" + str(AlertNotes)
                AlertStatus = 'FALSE'
            else:
                if ExceptionCategory != "":
                    AlertNotes = 'Exception Exist for this OSM/Unit, please check if it needs to be considered :' + (
                        ExceptionCategory) + "\n\n" + str(AlertNotes)
                    AlertStatus = 'PENDING-READY'
                else:
                    PRJDuplicateCheckFlag, PRJExceptionFlag, PRJDuplicateCheckStatus, PRJCaseID = self.CheckPRJDuplicateCases(
                        OSMName)
                    if (PRJExceptionFlag == 1):
                        AlertStatus = 'False'
                        AlertNotes = PRJDuplicateCheckStatus

                    if (DuplicateCheckFlag == 1):
                        AlertNotes = 'MND Duplicate Case exist : \n' + str(CaseDetails) + "\n\n" + str(AlertNotes)
                        AlertStatus = 'DUPLICATE'
                    else:
                        ExistingCaseGroup = CaseDetails.split("\ni")
                        ExistingCaseGroup = ExistingCaseGroup[1:]
                        for eachCase in ExistingCaseGroup:
                            ExistingCaseGroup = eachCase.split("~")
                            ExistingCaseGroup = ExistingCaseGroup[2]
                            if ExistingCaseGroup.strip().upper() == 'Connectivity/Security'.upper():
                                AlertNotes = """MND Case exist for this OSM/Unit, please check if it needs to be considered as duplicate.\nDuplicate case details are as below:""" + "\n" + str(
                                    CaseDetails) + "\n" + str(AlertNotes)
                                AlertStatus = 'PENDING-READY'

            if str(AlertStatus).upper() not in ('FALSE', 'DUPLICATE'):
                AlertUpdate = ''
                if OSMIPAddress != "":
                    OSMIP_PingStatus, OSMIP_Loss = self.getipstatus(OSMIPAddress)
                    if int(OSMIP_Loss) <= 10:
                        OSMIP_PingStatus = "OSM IP ping status  is within threshold limit. Below is the ping Status\n" + OSMIP_PingStatus

                        AlertNotes = OSMIP_PingStatus
                        AlertStatus = 'NO ISSUE FOUND'

                    else:
                        if int(OSMIP_Loss) > 10 and int(OSMIP_Loss) != 100:
                            OSMIP_PingStatus = "OSM IP ping status  is not within threshold limit. Below is the ping Status\n" + OSMIP_PingStatus
                            PingStatusFlag = 1
                        else:
                            OSMIP_PingStatus = "OSM IP is not Pinging Back. Below is the ping Status\n" + OSMIP_PingStatus
                            PingStatusFlag = 1

                        if iLO_GE_IP != "" and iLO_GE_IP != 'N/A':
                            iLO_GE_IP_PingStatus, iLO_GE_IP_Loss = self.getipstatus(iLO_GE_IP)

                            if int(iLO_GE_IP_Loss) == 100:
                                iLO_GE_IP_PingStatus = "iLO_GE IP is not Pinging Back. Below is the ping Status\n" + iLO_GE_IP_PingStatus
                            elif int(iLO_GE_IP_Loss) <= 10:
                                iLO_GE_IP_PingStatus = "iLO_GE IP ping status  is within threshold limit. Below is the ping Status\n" + iLO_GE_IP_PingStatus
                            else:
                                iLO_GE_IP_PingStatus = "iLO_GE IP ping status  is not within threshold limit. Below is the ping Status\n" + iLO_GE_IP_PingStatus
                        else:
                            iLO_GE_IP_PingStatus = "iLO GE IP is not available"
                            iLO_GE_IP_Loss = ""

                        if HyperVisor_IP != "" and HyperVisor_IP is not None and HyperVisor_IP != 'N/A':
                            HyperVisor_IP_PingStatus, HyperVisor_IP_Loss = self.getipstatus(HyperVisor_IP)
                            if int(HyperVisor_IP_Loss) == 100:
                                HyperVisor_IP_PingStatus = "HyperVisor IP is not Pinging Back. Below is the ping Status\n" + HyperVisor_IP_PingStatus
                            elif int(HyperVisor_IP_Loss) <= 10:
                                HyperVisor_IP_PingStatus = "HyperVisor IP ping status  is within threshold limit. Below is the ping Status\n" + HyperVisor_IP_PingStatus
                            else:
                                HyperVisor_IP_PingStatus = "HyperVisor IP ping status  is not within threshold limit. Below is the ping Status\n" + HyperVisor_IP_PingStatus
                        else:
                            HyperVisor_IP_PingStatus = "HyperVisor IP is not available"
                            HyperVisor_IP_Loss = ""

                        if RouterIP != "" and RouterIP != 'N/A':
                            RouterIP_PingStatus, RouterIP_Loss = self.getipstatus(RouterIP)
                            if int(RouterIP_Loss) == 100:
                                RouterIP_PingStatus = "Router IP is not Pinging Back. Below is the ping Status\n" + RouterIP_PingStatus
                            elif int(RouterIP_Loss) <= 10:
                                RouterIP_PingStatus = "Router IP ping status  is within threshold limit. Below is the ping Status\n" + RouterIP_PingStatus
                            else:
                                RouterIP_PingStatus = "Router IP ping status  is not within threshold limit. Below is the ping Status\n" + RouterIP_PingStatus
                        else:
                            RouterIP_PingStatus = "Router IP is not available"
                            RouterIP_Loss = ""

                        if AlertStatus != 'PENDING-READY':
                            AlertStatus = 'IN-PROCESS'
                        AlertNotes = AlertNotes + "\n" + OSMIP_PingStatus + "\n" + iLO_GE_IP_PingStatus + "\n" + HyperVisor_IP_PingStatus + "\n" + RouterIP_PingStatus
                        # TODO After check need to uncomment line 728 - 730
                if SolarWindFlag == 1:
                    logging.info("Solar wind")
                    AlertNotes = str(AlertNotes)
                    self.UpdateConnectivityAlert(EquipmentAlarmID, AlertNotes, AlertStatus, OSMIPMismatch)
                else:
                    AlertUpdate, DatapointsFlag = self.CheckDatapoints(EquipmentSrNo)
                    if DatapointsFlag == 1:
                        AlarmName = 'APM-Controller Data Availability Unhealthy - TNH'
                        IDSMapping = self.GetIDSMapping(AlarmName)
                        DuplicateCheckFlag, CaseDetails, Status = self.CheckMNDDuplicateCases(OSMName, IDSMapping)
                        PRJDuplicateCheckFlag, PRJExceptionFlag, PRJDuplicateCheckStatus, PRJCaseID = self.CheckPRJDuplicateCases(
                            OSMName)
                        if (PRJExceptionFlag == 1):
                            AlertStatus = 'False'
                            AlertNotes = PRJDuplicateCheckStatus

                        if (DuplicateCheckFlag == 1):
                            AlertNotes = 'MND Duplicate Case exist for Data Not Archiving Issue : \n' + str(
                                CaseDetails) + "\n\n" + str(AlertUpdate) + "\n\n" + str(AlertNotes)
                            AlertStatus = 'DUPLICATE'
                        else:
                            if Status != '':
                                AlertNotes = """MND Case exist for this OSM/Unit, please check if it needs to be considered as duplicate.\nDuplicate case details are as below:""" + "\n" + str(
                                    CaseDetails) + "\n\n" + str(AlertUpdate) + "\n\n" + str(AlertNotes)
                                AlertStatus = 'PENDING-READY'
                            else:
                                AlertStatus = 'PENDING-READY'
                                FinalComments = 'Move to Pending-Ready as issue with Datapoints and not with Ping.'
                                AlertNotes = str(AlertUpdate) + "\n" + str(AlertNotes)

                    # self.UpdateConnectivityAlert(EquipmentAlarmID, AlertNotes, AlertStatus, OSMIPMismatch)
                    if alertValidationFlag == 1 and AlertStatus.upper().strip() == 'IN-PROCESS':
                        # TODO local var issue - line no : 671
                        AlertUpdate = "Received multiple alerts for same OSM. Please validate the alert manually." + "\n" + AlertUpdate
                        AlertStatus = 'PENDING-READY'
                    if alertValidationFlag == 2 and AlertStatus.upper().strip() == 'IN-PROCESS':
                        AlertUpdate = "We have multiple alert's from the same site for different OSM's.Please validate the alert manually." + "\n" + AlertUpdate
                        AlertStatus = 'PENDING-READY'

            NotesPrefix = self.GetNotesPrefix()
            AlertUpdate = NotesPrefix + AlertUpdate
            AlertUpdate = AlertUpdate.replace("'", "")
            AlertNotes = AlertUpdate + "\n" + "Alert Status : " + AlertStatus
            self.UpdateConnectivityAlert(EquipmentAlarmID, AlertNotes, AlertStatus, OSMIPMismatch)