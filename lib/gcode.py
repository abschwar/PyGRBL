#!/usr/bin/env python
# gcode.py : Parses a gcode file
# [2012.07.31] Mendez
import re,sys
from string import Template
from pprint import pprint
from clint.textui import colored, puts, indent, progress

CMDS='GXYZMP'

TEMPLATE='''(UPDATED by ${tag})
${init}
${gcode}'''

class GCode(list):
  def __init__(self, gcode):
    '''start with a gcode ascii file'''
    if isinstance(gcode, str):
      with open(gcode,'r') as f:
        lines = f.readlines()
        filename = gcode
    else:
      filename = gcode.name
      lines = gcode.readlines()
      gcode.close()
    self.filename = filename
    self.lines = lines
    self.ready = False
  
  def append(self,item):
    '''add the next nice to the object'''
    if self.ready : self.ready = False
    super(GCode, self).append(item)
  
  def parse(self):
    '''By default .parse() grabs only the G## commands for creating toolpaths in some space
    if you need everything use .parseall()'''
    everything = self._parse()
    for item in everything:
      for cmd in CMDS:
        if cmd in item:
          self.append(item)
  
  def parseAll(self):
    '''Gets everything so that we can print it back out'''
    everything = self._parse()
    for item in everything:
      self.append(item)
  
  def _parse(self):
    ''' [INTERNAL] convert the readlines into a parsed set of commands and values'''
    puts(colored.blue('Parsing gCode'))
    
    comment = r'\(.*?\)'
    whitespace = r'\s'
    command = r''.join([r'(?P<%s>%s(?P<%snum>-?\d+(?P<%sdecimal>\.?)\d*))?'%(c,c,c,c) for c in CMDS])
    output = []
    for i,line in enumerate(progress.bar(self.lines)):
    # for i,line in enumerate(self.lines):
      l = line.strip()
      # find comments, save them, and then remove them
      m = re.findall(comment,l)
      l = re.sub(whitespace+'|'+comment,'',l).strip().upper()
      # l = re.sub(whitespace,'',l).upper()

      # Grab the commands
      c = re.match(command,l)
      
      # output commands to a nice dict
      out = {}
      out['index'] = i
      # out['line'] = line
      if m: out['comment'] = m
      for cmd in CMDS:
        if c.group(cmd):
          # either a float if '.' or a int
          fcn = float if c.group(cmd+'decimal') else int
          out[cmd] = fcn(c.group(cmd+'num'))
          out['index'] = i
      if len(out) > 0:
        output.append(out)
    return output
      #     
      # if len(out) > 0:
      #   self.append(out)
  
  def update(self,tool):
    '''Updates the gcode with a toolpath only does x,y'''
    UPDATE = 'xy'
    for x in tool:
      # print len(x)
      if len(x) == 5:
        print x
        
        for u in UPDATE:
          if u.upper() in self[x[4]]:
            self[x[4]][u.upper()] = x[UPDATE.index(u)]
        print self[x[4]]
          # print self[x[4]], 
          # print u.upper(), 
          # print self[x[4]][u.upper()]
          # print self[x[4]][u.toupper()]#, x[UPDATE.index(u)]
          # print self[x[4]][u],x[UPDATE.index(u)]
            
  
  def getGcode(self,tag=__name__):
    lines = []
    for i,line in enumerate(self):
      l = ''
      for cmd in CMDS:
        if cmd in line:
          l += (' %s%.3f' if cmd in 'XYZ' else '%s%02i  ')%(cmd,line[cmd])
      # add in the comments
      if 'comment' in line: l += ' '.join(line['comment'])
      lines.append(l)
    params = dict(gcode='\n'.join(lines),
                  init='G20\nG91\nG00 X0.000 Y0.000 Z0.000\n(Begin)', # ensure we init things correctly
                  tag=tag)
    return Template(TEMPLATE).substitute(params)
    
      