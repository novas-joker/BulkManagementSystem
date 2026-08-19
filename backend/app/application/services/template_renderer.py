"""Service for rendering email templates with personalization and tracking."""

import re
from typing import Any


class TemplateRendererService:
    """Render email templates with variable substitution and tracking integration."""

    @staticmethod
    def replace_variables(content: str, variables: dict[str, Any]) -> str:
        """
        Replace template variables in format {{variable_name}} with actual values.
        Supports nested dict access via dot notation: {{user.first_name}}
        """
        if not content:
            return content

        def replace_var(match):
            var_name = match.group(1)
            value = TemplateRendererService._get_nested_value(variables, var_name)
            return str(value) if value is not None else match.group(0)

        return re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_var, content)

    @staticmethod
    def _get_nested_value(obj: dict, path: str) -> Any:
        """Get a value from nested dict using dot notation."""
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    @staticmethod
    def inject_tracking_pixel(html_content: str, campaign_id: str, contact_id: str) -> str:
        """
        Inject a tracking pixel URL at the end of the email body.
        Used to track email opens.
        """
        tracking_url = f"/track/open?campaign={campaign_id}&contact={contact_id}"
        tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" alt="" style="display:none;" />'

        # Try to inject before </body> tag
        if '</body>' in html_content.lower():
            return html_content.replace('</body>', f'{tracking_pixel}</body>')

        # Otherwise append at the end
        return html_content + tracking_pixel

    @staticmethod
    def inject_unsubscribe_link(html_content: str, contact_id: str, campaign_id: str) -> str:
        """
        Inject an unsubscribe link footer in the email.
        Required for CAN-SPAM compliance.
        """
        unsubscribe_url = f"/unsubscribe?contact={contact_id}&campaign={campaign_id}"
        unsubscribe_html = (
            f'<footer style="margin-top: 30px; font-size: 12px; color: #999;">'
            f'<p><a href="{unsubscribe_url}">Unsubscribe from this mailing list</a></p>'
            f'</footer>'
        )

        if '</body>' in html_content.lower():
            return html_content.replace('</body>', f'{unsubscribe_html}</body>')

        return html_content + unsubscribe_html

    @staticmethod
    def render_html(
        template_html: str,
        variables: dict[str, Any],
        campaign_id: str | None = None,
        contact_id: str | None = None,
        include_tracking: bool = True,
        include_unsubscribe: bool = True,
    ) -> str:
        """
        Render HTML template with variable substitution and optional tracking/unsubscribe.
        """
        # Replace variables
        rendered = TemplateRendererService.replace_variables(template_html, variables)

        # Inject tracking pixel
        if include_tracking and campaign_id and contact_id:
            rendered = TemplateRendererService.inject_tracking_pixel(rendered, campaign_id, contact_id)

        # Inject unsubscribe link
        if include_unsubscribe and contact_id and campaign_id:
            rendered = TemplateRendererService.inject_unsubscribe_link(rendered, contact_id, campaign_id)

        return rendered

    @staticmethod
    def render_text(
        template_text: str,
        variables: dict[str, Any],
    ) -> str:
        """
        Render plain text template with variable substitution.
        """
        return TemplateRendererService.replace_variables(template_text, variables)

    @staticmethod
    def validate_variables(content: str) -> list[str]:
        """
        Extract all template variables from content.
        Returns list of variable names found.
        """
        return re.findall(r'\{\{(\w+(?:\.\w+)*)\}\}', content)

    @staticmethod
    def preview_render(
        template_html: str,
        template_text: str,
    ) -> dict[str, str]:
        """
        Generate a preview of the template with sample data.
        Replaces all variables with [VARIABLE_NAME] placeholders.
        """
        def replace_vars(content):
            def replacer(match):
                var_name = match.group(1)
                return f"[{var_name.upper()}]"

            return re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replacer, content)

        return {
            "html": replace_vars(template_html),
            "text": replace_vars(template_text),
        }
