from sphinxcontrib.jinjagen.filegen import FileGenRunDef, GenKeyNode

extensions = ["sphinxcontrib.jinjagen"]
exclude_patterns = ["_build"]

templates_path = ['_templates']

#TODO make GenKeyLeaf
gen_key_tree_recipe: GenKeyNode = GenKeyNode("gen", [
    GenKeyNode('recipe_all_recipes', [
        GenKeyNode('french toast', []),
        GenKeyNode('chicken speedie', [])
    ]),
    GenKeyNode('recipe_youtube', [
        GenKeyNode('columbian stew', [])
    ])
])

recipe_run = FileGenRunDef([gen_key_tree_recipe], 'recipe', 'recipe.jinja', 'rst')

gen_key_tree_recipe_source: GenKeyNode = GenKeyNode("gen", [
    GenKeyNode('recipe_all_recipes', []),
    GenKeyNode('recipe_youtube', []),
    GenKeyNode('recipe_serious', [])
])

recipe_source_run = FileGenRunDef([gen_key_tree_recipe_source], 'recipe_source', 'recipe_source.jinja', 'rst')

jinjagen_runs = [recipe_run, recipe_source_run]
