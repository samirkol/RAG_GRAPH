class EntityService:

    def extract_entities(self, text: str):
        entities = []

        text_lower = text.lower()

        # ----------------------------------
        # Payment Terms
        # ----------------------------------

        payment_terms = [
            "net 30",
            "net 45",
            "net 60",
            "immediate"
        ]

        for term in payment_terms:

            if term in text_lower:

                entities.append({
                    "name": term.title(),
                    "type": "payment_term"
                })

        # ----------------------------------
        # Departments
        # ----------------------------------

        departments = [
            "finance",
            "procurement",
            "accounts payable",
            "legal"
        ]

        for department in departments:

            if department in text_lower:

                entities.append({
                    "name": department.title(),
                    "type": "department"
                })

        # ----------------------------------
        # Supplier Categories
        # ----------------------------------

        supplier_categories = [
            "selected suppliers",
            "strategic suppliers"
        ]

        for category in supplier_categories:

            if category in text_lower:

                display_name = (
                    "Selected Supplier"
                    if category == "selected suppliers"
                    else "Strategic Supplier"
                )

                entities.append({
                    "name": display_name,
                    "type": "supplier_category"
                })

        # ----------------------------------
        # Invoice
        # ----------------------------------

        if "invoice" in text_lower:

            entities.append({
                "name": "Invoice",
                "type": "document_type"
            })

        # ----------------------------------
        # Non-Compliant Invoice
        # ----------------------------------

        if (
            "non-compliant invoice" in text_lower
            or "non-compliant invoices" in text_lower
            or "invoice standards" in text_lower
        ):

            entities.append({
                "name": "Non-Compliant Invoice",
                "type": "invoice_status"
            })

        # ----------------------------------
        # Invoice Hold
        # ----------------------------------

        if (
            "placed on hold" in text_lower
            or "invoice hold" in text_lower
        ):

            entities.append({
                "name": "Invoice Hold",
                "type": "invoice_action"
            })

        # ----------------------------------
        # Invoice Requirements
        # ----------------------------------

        invoice_requirements = [
            "purchase order number",
            "supplier information",
            "invoice date",
            "currency",
            "tax details",
            "line-item references"
        ]

        for requirement in invoice_requirements:

            if requirement in text_lower:

                entities.append({
                    "name": requirement.title(),
                    "type": "invoice_requirement"
                })

        return entities