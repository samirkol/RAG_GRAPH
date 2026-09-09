class RelationshipService:

    def extract_relationships(self, text: str):

        relationships = []

        text_lower = text.lower()

        # ----------------------------------
        # Immediate Payment
        # ----------------------------------

        if "immediate payment" in text_lower:

            if "finance" in text_lower:

                relationships.append({
                    "source": "Immediate",
                    "source_type": "payment_term",
                    "relationship": "requires_approval",
                    "target": "Finance",
                    "target_type": "department"
                })

            if "procurement" in text_lower:

                relationships.append({
                    "source": "Immediate",
                    "source_type": "payment_term",
                    "relationship": "requires_approval",
                    "target": "Procurement",
                    "target_type": "department"
                })

        # ----------------------------------
        # Net 60
        # ----------------------------------

        if (
            "net 60" in text_lower
            and "strategic suppliers" in text_lower
        ):

            relationships.append({
                "source": "Net 60",
                "source_type": "payment_term",
                "relationship": "may_apply_to",
                "target": "Strategic Supplier",
                "target_type": "supplier_category"
            })

        # ----------------------------------
        # Net 45
        # ----------------------------------

        if (
            "net 45" in text_lower
            and (
                "selected suppliers" in text_lower
                or "selected supplier" in text_lower
            )
        ):

            relationships.append({
                "source": "Net 45",
                "source_type": "payment_term",
                "relationship": "may_apply_to",
                "target": "Selected Supplier",
                "target_type": "supplier_category"
            })

        # ----------------------------------
        # Non-Compliant Invoice
        # ----------------------------------

        if (
            "non-compliant invoice" in text_lower
            or "non-compliant invoices" in text_lower
        ):

            if "placed on hold" in text_lower:

                relationships.append({
                    "source": "Non-Compliant Invoice",
                    "source_type": "invoice_status",
                    "relationship": "may_be_placed_on_hold",
                    "target": "Invoice Hold",
                    "target_type": "invoice_action"
                })

        # ----------------------------------
        # Invoice Requirements
        # ----------------------------------

        if "invoice" in text_lower:

            invoice_fields = [
                "purchase order number",
                "supplier information",
                "invoice date",
                "currency",
                "tax details",
                "line-item references"
            ]

            for field in invoice_fields:

                if field in text_lower:

                    relationships.append({
                        "source": "Invoice",
                        "source_type": "document_type",
                        "relationship": "requires",
                        "target": field.title(),
                        "target_type": "invoice_requirement"
                    })

        return relationships