# 1st

v = vte.Terminal()
v.fork_command('bash')
v.feed_child('ssh %s tail -f %s.o%s \n' % (host,jname,id))
v.show()
notebook.append_page(v, tab_label=gtk.Label(nodeid))

# 2nd


