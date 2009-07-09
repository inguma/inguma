#!/usr/bin/python
"""
Inguma Penetration Testing Toolkit
Copyright (c) 2006, 2007 Joxean Koret, joxeankoret [at] yahoo.es

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
"""
NOTE: Will be removed surely some day as is useless currently
"""
import sys

WINNT = 0
WIN2K_SP0 = 1
WIN2K_SP1 = 2
WIN2K_SP2 = 3
WIN2K_SP3 = 4
WIN2K_SP4 = 5
WINXP_SP0 = 6
WINXP_SP1 = 7
WINXP_SP2 = 8
WIN2K3_SP0 = 9
WIN2K3_SP1 = 10
WINVISTA = 11

uuids = {}
uuids["86d35949-83c9-4044-b424-db363231fd0c"] = {name:"ITaskSchedulerService", os:(WINVISTA, ), version:"1.0"}
uuids["0a74ef1c-41a4-4e06-83ae-dc74fb1cdd53"] = {name:"idletask", os:(WINXP_SP0, WINXP_SP1, WINXP_SP2, WIN2K3_SP0, WIN2K3_SP1), version:"1.0"}
uuids["76209FE5-9049-4336-BA84-632D907CB154"] = {name:"ReportingServices$MSSQL.2", os:(WIN2K3_SP0, WIN2K3_SP1), version:"1.0"}
uuids["1ff70682-0a51-30e8-076d-740be8cee98b"] = {name:"atsvc", os:(WINXP_SP0, WINXP_SP1, WINXP_SP2, WIN2K3_SP0, WIN2K3_SP1), version:"1.0"}
uuids["378e52b0-c0a9-11cf-822d-00aa0051e40f"] = {name:"sasec", os:(WINXP_SP0, WINXP_SP1, WINXP_SP2, WIN2K3_SP0, WIN2K3_SP1), version:"1.0"}
uuids["3faf4738-3a21-4307-b46c-fdda9bb8c0d5"] = {name:"audiosrv", os:(WIN2K3_SP0, WIN2K3_SP1), version:"1.0"}
