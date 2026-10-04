from EGraph.EGraph import EGraph


class EGraphSynthesizer:
    def __init__(self, decoder, semantic_matcher):
        self.decoder = decoder
        self.matcher = semantic_matcher
        self.primitives = MasterPrimitiveRegistry()

    def synthesize(self, spss_ast, expected_type: DateType, max_iterations: int = 3) -> str:
        egraph = EGraph()
        root_id = ingest_spss_ast(egraph, spss_ast, self.decoder, self.matcher, self.primitives)

        rewriter = RewriteRule()
        for _ in range(max_iterations):
            if not rewriter.apply(egraph, self.primitives):
                break

        extractor = EGraphExtractor(egraph, self.primitives)
        result = extractor.extract(root_id, expected_type)

        return result.code