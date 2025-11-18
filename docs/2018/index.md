---
layout: default
title: Advent of Code 2018
---
# {{ page.topic}} {{ page.year }}

Welcome to [AoC 2018](https://adventofcode.com/2018){:target="_blank"}!

"We've detected some temporal anomalies," one of Santa's Elves tells you.

Ready to save Christmas?  Follow the links below.

## Day Index

<ol>
  {% assign the_year = site.data.navigation.pages | where: 'name', page.year %}
  {% for member in the_year[0].members %}
      <li><a href="{{ member.link | absolute_url }}">{{ member.problem }}</a></li>
  {% endfor %}
</ol>
