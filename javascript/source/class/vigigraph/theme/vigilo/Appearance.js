/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2004-2007 1&1 Internet AG, Germany, http://www.1and1.org

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Sebastian Werner (wpbasti)
     * Andreas Ecker (ecker)

************************************************************************ */

/**
 * Vigilo color theme
 */
qx.Theme.define("vigigraph.theme.vigilo.Appearance",
{
  title : "Vigilo Appearance",
  extend: qx.theme.classic.Appearance,

  appearances:
  {
    "client-document":
    {
      base: true,

      style: function(states)
      {
        return {
          backgroundColor : "vigilobg"
        };
      }
    }
  }

});


// vim: set tabstop=2 shiftwidth=2 expandtab :
