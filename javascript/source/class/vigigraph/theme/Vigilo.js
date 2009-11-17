/* ************************************************************************

   Vigigraph User Interface
   Copyright: 2007-2009 CS-SI <http://www.c-s.fr>

   License: GPLv2+

   Authors: Arnaud MAZIN <arnaud.mazin@c-s.fr>
            Aurelien BOMPARD <aurelien.bompard@c-s.fr>
            Thomas BURGUIERE <thomas.burguiere@c-s.fr>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
  
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
  
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

************************************************************************ */

qx.Theme.define("vigigraph.theme.Vigilo",
{
  title : "Vigilo",
//  extend : qx.theme.ClassicRoyale,
 
  meta :
  {
    //color : qx.theme.classic.color.Royale,
    color : vigigraph.theme.vigilo.Colors,
    border : qx.theme.classic.Border,
    font : qx.theme.classic.font.Default,
    widget : qx.theme.classic.Widget,
    //appearance : qx.theme.classic.Appearance,
    appearance : vigigraph.theme.vigilo.Appearance,
    icon : qx.theme.icon.Nuvola
  }

});


// vim: set tabstop=2 shiftwidth=2 expandtab :
