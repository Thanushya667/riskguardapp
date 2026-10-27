import smtplib
from html import escape
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config


class EmailService:

    @staticmethod
    def is_configured():
        """Check whether SMTP settings are available."""
        return bool(
            getattr(Config, "SMTP_HOST", None)
            and getattr(Config, "SMTP_USERNAME", None)
            and getattr(Config, "SMTP_PASSWORD", None)
            and getattr(Config, "SENDER_EMAIL", None)
        )

    @classmethod
    def send_risk_alert_email(
        cls,
        student_name,
        student_email,
        risk_level,
        risk_factors,
        recommendations,
        prediction_date=None,
        acknowledgement_url=None,
        tracking_reference=None
    ):
        """
        Send an academic risk alert.

        Returns:
            ("SENT", message)
            ("FAILED", message)
            ("NOT_CONFIGURED", message)

        acknowledgement_url is optional.
        """

        if not cls.is_configured():
            return (
                "NOT_CONFIGURED",
                "SMTP credentials are not configured."
            )

        if risk_level not in (
            "High Risk",
            "Medium Risk",
            "Low Risk"
        ):
            return (
                "FAILED",
                f"Unsupported risk level: {risk_level}"
            )

        if not student_email or "@" not in student_email:
            return (
                "FAILED",
                "A valid student email address is required."
            )

        server = None

        try:
            # -------------------------------------------------
            # RISK-LEVEL CONTENT
            # -------------------------------------------------

            if risk_level == "High Risk":
                subject = (
                    "Academic Risk Alert - Immediate Attention "
                    "Required (High Risk)"
                )
                intro_message = (
                    "Your current academic performance indicates "
                    "a High Risk level. Immediate academic attention "
                    "and intervention are recommended."
                )
                closing_message = (
                    "Please contact your faculty mentor or department "
                    "advisor immediately to discuss academic support."
                )
                header_title = "Academic Risk Alert"
                header_subtitle = "Immediate Attention Required"
                risk_color = "#c0392b"

            elif risk_level == "Medium Risk":
                subject = (
                    "Academic Performance Alert - Improvement "
                    "Recommended (Medium Risk)"
                )
                intro_message = (
                    "Your current academic performance indicates "
                    "a Medium Risk level. Please focus on improving "
                    "your academic performance and maintaining progress."
                )
                closing_message = (
                    "Continue working with your faculty mentor and "
                    "focus on the recommended academic improvements."
                )
                header_title = "Academic Performance Alert"
                header_subtitle = "Improvement Recommended"
                risk_color = "#c48a47"

            else:
                subject = (
                    "Congratulations! Your Academic Performance "
                    "is Good (Low Risk)"
                )
                intro_message = (
                    "Congratulations! Your current academic "
                    "performance places you in the Low Risk category. "
                    "Good job! Keep maintaining your performance."
                )
                closing_message = (
                    "Continue attending classes regularly, submitting "
                    "assignments on time, and maintaining consistent "
                    "academic progress."
                )
                header_title = "Congratulations!"
                header_subtitle = "Excellent Academic Performance"
                risk_color = "#285743"
                if tracking_reference:
                      subject = f"{subject} [RiskGuard Ref: {tracking_reference}]"

            # -------------------------------------------------
            # NORMALIZE FACTORS AND RECOMMENDATIONS
            # -------------------------------------------------

            if isinstance(risk_factors, (list, tuple)):
                factors = list(risk_factors)
            elif risk_factors:
                factors = [risk_factors]
            else:
                factors = [
                    "Academic performance requires attention."
                ]

            if isinstance(recommendations, (list, tuple)):
                recs = list(recommendations)
            elif recommendations:
                recs = [recommendations]
            else:
                recs = [
                    "Meet with your faculty mentor.",
                    "Monitor your academic progress regularly."
                ]

            if risk_level == "Low Risk":
                recs = [
                    "Maintain your good academic performance.",
                    "Continue attending classes regularly.",
                    "Submit assignments on time.",
                    "Maintain consistent academic progress."
                ]

            # -------------------------------------------------
            # ESCAPE DYNAMIC HTML VALUES
            # -------------------------------------------------

            safe_name = escape(str(student_name or "Student"))
            safe_risk = escape(str(risk_level))
            safe_intro = escape(intro_message)
            safe_closing = escape(closing_message)
            safe_date = escape(
                str(prediction_date or "Recent Evaluation")
            )
            safe_header = escape(header_title)
            safe_subtitle = escape(header_subtitle)

            factors_html = "".join(
                f"<li style='margin-bottom:6px;'>"
                f"{escape(str(item))}</li>"
                for item in factors
            )

            recs_html = "".join(
                f"<li style='margin-bottom:6px;'>"
                f"{escape(str(item))}</li>"
                for item in recs
            )

            factors_text = "\n".join(
                f"- {item}" for item in factors
            )
            recs_text = "\n".join(
                f"- {item}" for item in recs
            )

            # -------------------------------------------------
            # OPTIONAL ACKNOWLEDGEMENT BUTTON
            # -------------------------------------------------

            acknowledgement_html = ""
            acknowledgement_text = ""

            if acknowledgement_url:
                parsed_url = urlparse(acknowledgement_url)

                # Only allow HTTP/HTTPS acknowledgement links.
                if parsed_url.scheme not in ("http", "https"):
                    return (
                        "FAILED",
                        "Acknowledgement URL must use HTTP or HTTPS."
                    )

                if not parsed_url.netloc:
                    return (
                        "FAILED",
                        "Acknowledgement URL is invalid."
                    )

                safe_url = escape(
                    acknowledgement_url,
                    quote=True
                )

                acknowledgement_html = f"""
                <div style="
                    margin:24px 0;
                    padding:18px;
                    background:#f1f5f9;
                    border-radius:6px;
                    text-align:center;
                ">
                    <p style="color:#334155;line-height:1.6;">
                        Please confirm that you have read this
                        academic notification.
                    </p>

                    <a href="{safe_url}" style="
                        display:inline-block;
                        background:#16382C;
                        color:#ffffff;
                        padding:12px 20px;
                        text-decoration:none;
                        border-radius:5px;
                        font-weight:600;
                    ">
                        I HAVE READ THIS ALERT
                    </a>
                </div>
                """

                acknowledgement_text = (
                    "\nAcknowledge this notification using the link:\n"
                    f"{acknowledgement_url}\n"
                )

            # -------------------------------------------------
            # PLAIN-TEXT EMAIL
            # -------------------------------------------------

            plain_body = f"""Dear {student_name or 'Student'},

This is an automated notification from RiskGuard Academic Risk Intelligence System.

Risk Level: {risk_level}
Date: {prediction_date or 'Recent Evaluation'}

{intro_message}

Academic Performance Indicators:
{factors_text}

Recommended Actions:
{recs_text}

{closing_message}
{acknowledgement_text}

Sincerely,
Academic Risk & Mentoring Committee
RiskGuard Intelligence
"""

            # -------------------------------------------------
            # HTML EMAIL
            # -------------------------------------------------

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="
                font-family:Segoe UI,Tahoma,Verdana,sans-serif;
                color:#1e293b;
                background:#f8fafc;
                padding:20px;
            ">
                <div style="
                    max-width:600px;
                    margin:0 auto;
                    background:#ffffff;
                    border-radius:8px;
                    border:1px solid #e2e8f0;
                    overflow:hidden;
                ">
                    <div style="
                        background:#16382C;
                        padding:24px;
                        color:#ffffff;
                    ">
                        <h2 style="margin:0;font-size:22px;">
                            RiskGuard | {safe_header}
                        </h2>
                        <p style="margin:6px 0 0;font-size:13px;">
                            {safe_subtitle}
                        </p>
                    </div>

                    <div style="padding:26px;">
                        <p>Dear <strong>{safe_name}</strong>,</p>

                        <p style="line-height:1.6;">
                            {safe_intro}
                        </p>

                        <div style="
                            background:#f1f5f9;
                            padding:16px;
                            border-radius:6px;
                            margin:20px 0;
                        ">
                            <div style="
                                font-size:13px;
                                color:#64748b;
                                margin-bottom:5px;
                            ">
                                Current Risk Level
                            </div>
                            <div style="
                                font-size:20px;
                                font-weight:700;
                                color:{risk_color};
                            ">
                                {safe_risk}
                            </div>
                            <div style="
                                font-size:12px;
                                color:#64748b;
                                margin-top:8px;
                            ">
                                Date: {safe_date}
                            </div>
                        </div>

                        <div style="
                            background:#f8fafc;
                            padding:16px 18px;
                            border-radius:6px;
                            margin:18px 0;
                        ">
                            <h4 style="margin:0 0 10px;">
                                Academic Performance Indicators
                            </h4>
                            <ul style="
                                margin:0;
                                padding-left:20px;
                                color:#334155;
                            ">
                                {factors_html}
                            </ul>
                        </div>

                        <div style="
                            background:#eaf3ed;
                            padding:16px 18px;
                            border-radius:6px;
                            margin:18px 0;
                        ">
                            <h4 style="
                                margin:0 0 10px;
                                color:#16382c;
                            ">
                                Recommended Actions
                            </h4>
                            <ul style="
                                margin:0;
                                padding-left:20px;
                                color:#285743;
                            ">
                                {recs_html}
                            </ul>
                        </div>

                        <p style="
                            font-size:14px;
                            color:#475569;
                            line-height:1.6;
                        ">
                            {safe_closing}
                        </p>

                        {acknowledgement_html}
                    </div>

                    <div style="
                        background:#f8fafc;
                        padding:14px 24px;
                        border-top:1px solid #e2e8f0;
                        font-size:12px;
                        color:#64748b;
                        text-align:center;
                    ">
                        RiskGuard Academic Risk Intelligence System
                        &bull; Automated Academic Notification
                    </div>
                </div>
            </body>
            </html>
            """

            # -------------------------------------------------
            # CREATE MESSAGE
            # -------------------------------------------------

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = Config.SENDER_EMAIL
            message["To"] = student_email

            message.attach(
                MIMEText(plain_body, "plain", "utf-8")
            )
            message.attach(
                MIMEText(html_body, "html", "utf-8")
            )

            # -------------------------------------------------
            # SMTP CONNECTION
            # -------------------------------------------------

            if Config.SMTP_USE_TLS:
                server = smtplib.SMTP(
                    Config.SMTP_HOST,
                    Config.SMTP_PORT,
                    timeout=10
                )
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                server = smtplib.SMTP_SSL(
                    Config.SMTP_HOST,
                    Config.SMTP_PORT,
                    timeout=10
                )

            server.login(
                Config.SMTP_USERNAME,
                Config.SMTP_PASSWORD
            )

            server.sendmail(
                Config.SENDER_EMAIL,
                [student_email],
                message.as_string()
            )

            print(
                f"EMAIL SENT SUCCESSFULLY: "
                f"{student_email} | {risk_level}"
            )

            return (
                "SENT",
                "Email successfully dispatched."
            )

        except Exception as error:
            print(f"SMTP Dispatch Error: {error}")

            return (
                "FAILED",
                str(error)
            )

        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass


# -------------------------------------------------------------
# GLOBAL EMAIL SERVICE INSTANCE
# -------------------------------------------------------------

email_service = EmailService()
