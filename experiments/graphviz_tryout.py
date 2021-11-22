from graphviz import Digraph
dot = Digraph(comment='Goal Tree')

# Goal
dot.node('0', 'Mein Leben erfüllen', shape='box', style='rounded')

# CSF
dot.node('1', 'Mein volles Potential für Gutes einsetzen',
         shape='box', style='rounded')
dot.node('2', 'Mein Leben selbstbestimmt gestalten',
         shape='box', style='rounded')

# NC
dot.node('1.1', 'Mein Potential entwickeln',
         shape='box', style='rounded')
dot.node('1.1.1', 'Bewusst und Commited sein',
         shape='box', style='rounded')
dot.node('1.1.1.1', 'Meditieren',
         shape='box', style='rounded')
dot.node('1.1.2', 'Mein Netzwerk entwickeln',
         shape='box', style='rounded')
dot.node('1.2', 'Klare Vorstellung dieses Guten haben',
         shape='box', style='rounded')
dot.node('1.2.1', 'Reflektieren',
         shape='box', style='rounded')
dot.node('2.1', 'Finanziell unabhängig sein',
         shape='box', style='rounded')
dot.node('2.2', 'Mich von Normen frei machen',
         shape='box', style='rounded')
dot.node('2.3', 'Spannende Dinge unternehmen',
         shape='box', style='rounded')
dot.node('2.3.1', 'Just Do It',
         shape='box', style='rounded')

# Edges
dot.edge('0', '1')
dot.edge('0', '2')
dot.edge('1', '1.1')
dot.edge('1.1', '1.1.1')
dot.edge('1.1.1', '1.1.1.1')
dot.edge('1.1', '1.1.2')
dot.edge('1', '1.2')
dot.edge('1.2', '1.2.1')
dot.edge('2', '2.1')
dot.edge('2', '2.2')
dot.edge('2', '2.3')
dot.edge('2.3', '2.3.1')

# Generate Output
print(dot.source)
dot.format = 'png'
dot.render(view=True)
