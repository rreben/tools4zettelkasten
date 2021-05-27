from graphviz import Digraph
dot = Digraph(comment='Goal Tree')

# Goal
dot.node('0', 'Ein erfülltes Leben führen', shape='box', style='rounded')

# CSF
dot.node('1', 'Sein volles Potential für Gutes einsetzen',
         shape='box', style='rounded')
dot.node('2', 'Sein Leben selbstbestimmt gestalten',
         shape='box', style='rounded')

# NC
dot.node('1.1', 'Sein Potential entwickeln',
         shape='box', style='rounded')
dot.node('2.1', 'finanziell unabhängig sein',
         shape='box', style='rounded')

# Edges
dot.edge('0', '1')
dot.edge('0', '2')
dot.edge('1', '1.1')
dot.edge('2', '2.1')

# Generate Output
print(dot.source)
dot.format = 'png'
dot.render(view=True)
