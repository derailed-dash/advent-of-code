---
layout: default
title: Advent of Code 2026
---
# {{ page.topic }} {{ page.year }}

<img src="{{ '/assets/images/AoC-collect-stars.png' | relative_url }}" alt="Advent of Code 2026" style="margin:15px 10px 10px 15px; float: right; width:225px" />

Welcome to [AoC 2026](https://adventofcode.com/2026){:target="_blank"}!

Following the 12-day format introduced in 2025, I'll publish my Python walkthroughs and visualisations here as the December puzzles unlock. In the meantime, check out [last year's solutions](/2025/) or browse [The Python Journey](/python/).

## Day Index

<ol>
  {% assign year_str = page.year | append: "" %}
  {% assign the_year = site.data.navigation.pages | where: 'name', year_str %}
  {% for member in the_year[0].members %}
      <li><a href="{{ member.link | relative_url }}">{{ member.problem }}</a></li>
  {% endfor %}
</ol>
