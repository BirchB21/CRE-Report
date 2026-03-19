"""
email_template.py
Builds the black-and-gold HTML email for the CRE Market Intelligence Report.
"""

from datetime import datetime


SECTOR_EMOJIS = {
    "office": "🏢",
    "retail": "🛍️",
    "industrial": "🏭",
    "multifamily": "🏠",
    "hospitality": "🏨",
    "healthcare": "🏥",
    "data centers": "💻",
}

SECTOR_COLORS = {
    "office":       "#C9A84C",
    "retail":       "#D4AF37",
    "industrial":   "#B8962E",
    "multifamily":  "#CFB53B",
    "hospitality":  "#C5A028",
    "healthcare":   "#DAA520",
    "data centers": "#E5C100",
}


def build_html_email(
    top_trends: str,
    sector_reports: dict,
    overall_summary: str,
    predictions: str,
) -> str:
    date_str = datetime.now().strftime("%A, %B %d, %Y")

    # ── Sector blocks ──────────────────────────────────────────────────────────
    sector_blocks = ""
    for sector, report in sector_reports.items():
        emoji = SECTOR_EMOJIS.get(sector, "📌")
        accent = SECTOR_COLORS.get(sector, "#D4AF37")
        label = sector.upper()

        # Format report text: turn "**bold**" markdown into <strong> tags
        import re
        formatted = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", report)
        # Turn numbered/bulleted lines into styled paragraphs
        paragraphs = ""
        for line in formatted.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "-", "•", "*")):
                clean = re.sub(r"^[\d\.\-\*\•]+\s*", "", line)
                paragraphs += f"""
                <tr>
                  <td style="padding:4px 0 4px 0;">
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      <tr>
                        <td width="12" valign="top" style="color:{accent};font-size:14px;padding-top:2px;">▸</td>
                        <td style="color:#D0D0D0;font-family:Georgia,serif;font-size:14px;line-height:1.7;padding-left:6px;">{clean}</td>
                      </tr>
                    </table>
                  </td>
                </tr>"""
            else:
                paragraphs += f"""
                <tr>
                  <td style="color:#D0D0D0;font-family:Georgia,serif;font-size:14px;line-height:1.8;padding:4px 0;">{line}</td>
                </tr>"""

        sector_blocks += f"""
        <!-- SECTOR: {label} -->
        <tr>
          <td style="padding:0 0 28px 0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background-color:#111111;border:1px solid #2A2A2A;border-left:4px solid {accent};">
              <!-- Sector header -->
              <tr>
                <td style="padding:18px 24px 14px 24px;border-bottom:1px solid #222222;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td>
                        <span style="font-size:20px;">{emoji}</span>
                        <span style="font-family:'Palatino Linotype',Palatino,serif;font-size:17px;
                                     font-weight:bold;color:{accent};letter-spacing:2px;
                                     text-transform:uppercase;margin-left:10px;">{label}</span>
                      </td>
                      <td align="right">
                        <span style="display:inline-block;background:{accent};color:#0A0A0A;
                                     font-family:Georgia,serif;font-size:10px;font-weight:bold;
                                     letter-spacing:1px;padding:3px 10px;text-transform:uppercase;">SECTOR REPORT</span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <!-- Sector body -->
              <tr>
                <td style="padding:16px 24px 20px 24px;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    {paragraphs}
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    # ── Format top trends ──────────────────────────────────────────────────────
    import re
    trend_rows = ""
    for i, line in enumerate(top_trends.split("\n")):
        line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line.strip())
        if not line:
            continue
        line = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color:#D4AF37;'>\1</strong>", line)
        trend_rows += f"""
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #1E1E1E;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td width="32" valign="top" align="center"
                    style="font-family:Georgia,serif;font-size:13px;font-weight:bold;
                           color:#0A0A0A;background:#D4AF37;padding:2px 0;min-width:26px;
                           text-align:center;">&nbsp;{i+1:02d}&nbsp;</td>
                <td style="color:#E0E0E0;font-family:Georgia,serif;font-size:14px;
                           line-height:1.7;padding-left:14px;">{line}</td>
              </tr>
            </table>
          </td>
        </tr>"""

    # ── Format summary & predictions ──────────────────────────────────────────
    def format_section(text):
        out = ""
        for line in text.split("\n"):
            line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line.strip())
            line = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color:#D4AF37;'>\1</strong>", line)
            if line:
                out += f'<p style="color:#D0D0D0;font-family:Georgia,serif;font-size:14px;line-height:1.8;margin:0 0 10px 0;">{line}</p>'
        return out

    summary_html = format_section(overall_summary)
    predictions_html = format_section(predictions)

    # ── Assemble full email ────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CRE Market Intelligence — {date_str}</title>
</head>
<body style="margin:0;padding:0;background-color:#050505;">

<!-- OUTER WRAPPER -->
<table cellpadding="0" cellspacing="0" border="0" width="100%"
       style="background-color:#050505;min-width:320px;">
  <tr>
    <td align="center" style="padding:32px 16px 48px 16px;">

      <!-- MAIN CONTAINER -->
      <table cellpadding="0" cellspacing="0" border="0" width="680"
             style="max-width:680px;width:100%;background-color:#0A0A0A;
                    border:1px solid #1F1F1F;border-top:3px solid #D4AF37;">

        <!-- ═══════════════════════════════════════════════════ HEADER -->
        <tr>
          <td style="padding:0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <!-- Gold gradient bar -->
              <tr>
                <td height="4" style="background:linear-gradient(90deg,#7B5A00,#D4AF37,#F5D87A,#D4AF37,#7B5A00);font-size:0;line-height:0;">&nbsp;</td>
              </tr>
              <tr>
                <td style="background-color:#0D0D0D;padding:36px 40px 28px 40px;
                           border-bottom:1px solid #1A1A1A;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td>
                        <div style="font-family:'Palatino Linotype',Palatino,serif;
                                    font-size:11px;letter-spacing:4px;color:#7B6A2A;
                                    text-transform:uppercase;margin-bottom:8px;">Daily Intelligence Briefing</div>
                        <div style="font-family:'Palatino Linotype',Palatino,serif;
                                    font-size:30px;font-weight:bold;color:#D4AF37;
                                    letter-spacing:1px;line-height:1.1;">CRE Market<br>
                          <span style="color:#F0E0A0;">Intelligence Report</span>
                        </div>
                      </td>
                      <td align="right" valign="top">
                        <div style="font-family:Georgia,serif;font-size:11px;
                                    color:#5A5A5A;letter-spacing:1px;text-align:right;">
                          {datetime.now().strftime("%B %d, %Y")}<br>
                          <span style="color:#3A3A3A;">6:00 AM EST</span>
                        </div>
                        <div style="margin-top:12px;border:1px solid #2A2000;
                                    background:#0F0C00;padding:6px 12px;
                                    font-family:Georgia,serif;font-size:10px;
                                    color:#8A7030;letter-spacing:2px;text-transform:uppercase;">
                          Powered by Claude AI
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ═══════════════════════════════════════════════ TOP TRENDS -->
        <tr>
          <td style="padding:32px 40px 8px 40px;">
            <!-- Section label -->
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="padding-bottom:16px;">
                  <table cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td style="background:#D4AF37;width:4px;font-size:0;">&nbsp;</td>
                      <td style="padding-left:14px;">
                        <span style="font-family:'Palatino Linotype',Palatino,serif;
                                     font-size:11px;letter-spacing:3px;color:#D4AF37;
                                     text-transform:uppercase;font-weight:bold;">Today's Most Important Trends</span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <!-- Trends card -->
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background:#0E0E0E;border:1px solid #252010;">
              <tr>
                <td style="padding:20px 24px 10px 24px;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    {trend_rows}
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Divider -->
        <tr>
          <td style="padding:28px 40px 4px 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="border-top:1px solid #1A1A1A;font-size:0;">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ════════════════════════════════════════════ SECTOR LABEL -->
        <tr>
          <td style="padding:12px 40px 20px 40px;">
            <table cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="background:#D4AF37;width:4px;font-size:0;">&nbsp;</td>
                <td style="padding-left:14px;">
                  <span style="font-family:'Palatino Linotype',Palatino,serif;
                               font-size:11px;letter-spacing:3px;color:#D4AF37;
                               text-transform:uppercase;font-weight:bold;">Sector-by-Sector Analysis</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ══════════════════════════════════════════ SECTOR BLOCKS -->
        <tr>
          <td style="padding:0 40px 0 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              {sector_blocks}
            </table>
          </td>
        </tr>

        <!-- Divider -->
        <tr>
          <td style="padding:4px 40px 28px 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="border-top:1px solid #1A1A1A;font-size:0;">&nbsp;</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ════════════════════════════════════════ OVERALL SUMMARY -->
        <tr>
          <td style="padding:0 40px 8px 40px;">
            <table cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="background:#D4AF37;width:4px;font-size:0;">&nbsp;</td>
                <td style="padding-left:14px;">
                  <span style="font-family:'Palatino Linotype',Palatino,serif;
                               font-size:11px;letter-spacing:3px;color:#D4AF37;
                               text-transform:uppercase;font-weight:bold;">Overall Market Summary</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 40px 32px 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background:#0D0D0D;border:1px solid #1E1E1E;border-left:4px solid #D4AF37;">
              <tr>
                <td style="padding:24px 28px;">
                  {summary_html}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ══════════════════════════════════════════════ PREDICTIONS -->
        <tr>
          <td style="padding:0 40px 8px 40px;">
            <table cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="background:#7B5A00;width:4px;font-size:0;">&nbsp;</td>
                <td style="padding-left:14px;">
                  <span style="font-family:'Palatino Linotype',Palatino,serif;
                               font-size:11px;letter-spacing:3px;color:#A88020;
                               text-transform:uppercase;font-weight:bold;">Forward Outlook &amp; Predictions</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 40px 40px 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background:#080800;border:1px solid #1E1800;border-left:4px solid #7B5A00;">
              <tr>
                <td style="padding:24px 28px;">
                  {predictions_html}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ═══════════════════════════════════════════════════ FOOTER -->
        <tr>
          <td style="background:#060606;border-top:1px solid #1A1A1A;padding:24px 40px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td>
                  <div style="font-family:Georgia,serif;font-size:11px;color:#3A3A3A;line-height:1.7;">
                    <span style="color:#5A4A10;">CRE Market Intelligence</span> · Auto-generated daily at 6:00 AM EST<br>
                    Powered by Claude AI &amp; live news aggregation · For informational purposes only
                  </div>
                </td>
                <td align="right" valign="middle">
                  <div style="font-family:'Palatino Linotype',Palatino,serif;
                              font-size:18px;color:#2A2000;letter-spacing:2px;">◆ CRE</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Bottom gold bar -->
        <tr>
          <td height="3" style="background:linear-gradient(90deg,#7B5A00,#D4AF37,#F5D87A,#D4AF37,#7B5A00);font-size:0;line-height:0;">&nbsp;</td>
        </tr>

      </table>
      <!-- /MAIN CONTAINER -->

    </td>
  </tr>
</table>

</body>
</html>"""

    return html
