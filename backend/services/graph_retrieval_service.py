class GraphRetrievalService:

    def find_entity_by_name(self, graph, entity_name):
        matches = []

        search_name = entity_name.lower().strip()

        for node_id, data in graph.nodes(data=True):

            node_name = data.get("name", "")

            if not node_name:
                continue

            if search_name == node_name.lower().strip():
                matches.append(node_id)

        return matches


    def get_related_entities(self, graph, entity_name):
        """
        Find entities directly connected FROM the requested entity.
        Example:

        Immediate
            -> requires_approval -> Finance
            -> requires_approval -> Procurement
        """

        entity_ids = self.find_entity_by_name(
            graph,
            entity_name
        )

        results = []

        for entity_id in entity_ids:

            for neighbor_id in graph.successors(entity_id):

                edge_data = graph.edges[
                    entity_id,
                    neighbor_id
                ]

                neighbor_data = graph.nodes[
                    neighbor_id
                ]

                results.append({
                    "source": graph.nodes[
                        entity_id
                    ].get("name", entity_id),

                    "relationship": edge_data.get(
                        "relationship"
                    ),

                    "target": neighbor_data.get(
                        "name",
                        neighbor_id
                    ),

                    "target_type": neighbor_data.get(
                        "type"
                    )
                })

        return results


    def get_related_entities_reverse(self, graph, entity_name):
        """
        Find entities connected TO the requested entity.

        Example:

        Net 45
            -> may_apply_to
            -> Selected Supplier

        Searching for "Selected Supplier" will return:

        Net 45 -> may_apply_to -> Selected Supplier
        """

        entity_ids = self.find_entity_by_name(
            graph,
            entity_name
        )

        results = []

        for entity_id in entity_ids:

            for neighbor_id in graph.predecessors(
                entity_id
            ):

                edge_data = graph.edges[
                    neighbor_id,
                    entity_id
                ]

                neighbor_data = graph.nodes[
                    neighbor_id
                ]

                results.append({
                    "source": neighbor_data.get(
                        "name",
                        neighbor_id
                    ),

                    "relationship": edge_data.get(
                        "relationship"
                    ),

                    "target": graph.nodes[
                        entity_id
                    ].get("name", entity_id),

                    "target_type": graph.nodes[
                        entity_id
                    ].get("type")
                })

        return results