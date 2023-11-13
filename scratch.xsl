<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:apply-templates select="queryRequest"/>
  </xsl:template>

  <xsl:template match="queryRequest">
    <xsl:text>/</xsl:text>
    <xsl:apply-templates select="collection"/>
    <xsl:apply-templates select="query"/>
  </xsl:template>

  <xsl:template match="query">
    <xsl:text>?</xsl:text>
    <xsl:apply-templates select="fields"/>
    <xsl:apply-templates select="where"/>
  </xsl:template>

  <xsl:template match="fields">
    <xsl:for-each select="*/column">
      <xsl:choose>
	<xsl:when test="position()=1">
	  <xsl:text>select=</xsl:text>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:text>,</xsl:text>
	</xsl:otherwise>
      </xsl:choose>
      <xsl:value-of select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="where">
    <xsl:for-each select="column">
      <xsl:text>&amp;</xsl:text>
      <xsl:
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
