# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HydroFileMaker
                                 A QGIS plugin
 Makes inSALMO Hydro File
                             -------------------
        begin                : 2016-10-28
        copyright            : (C) 2016 by Peter Dudley
        email                : pndphd@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load HydroFileMaker class from file HydroFileMaker.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .HydroFileMaker import HydroFileMaker
    return HydroFileMaker(iface)
