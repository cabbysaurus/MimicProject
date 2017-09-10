import scrapy

split_children = []


class IcdScraper(scrapy.Spider):
    name = 'icd'
    start_urls = ['http://www.icd9data.com/2015/Volume1/default.htm',]

    def parse(self, response):

        # get the list of ids and links that we care about from the page
        links = response.css('li a::attr(href)').re('/2015/Volume1/E?V?[0-9]*[-E?V?0-9/]+[default]*.htm')
        child_links = response.css('a.identifier::attr(href)').re('/2015/Volume1/E?V?[0-9]*[-E?V?0-9/]+E?V?[0-9]+\.?[0-9]*.htm')
        ids = response.css('ul a.identifier::text').extract()

        for id in ids:
            if len(child_links) > 0:
                for link in child_links:
                    split_child = str(link).split('/')
                    split_child.remove('')
                    split_child.remove('2015')
                    split_child.remove('Volume1')
                    split_child[len(split_child) - 1] = split_child[len(split_child) - 1].replace('.htm', '')
                    split_child.insert(0, 'root')

                    if '.' in split_child[len(split_child) - 1]:
                        split_element = split_child[len(split_child) - 1].split('.')
                        if len(split_element[1]) > 1:
                            parent = split_element[0] + '.' + split_element[1][0]
                            split_child.insert(len(split_child) - 1, parent)
                            #if parent not in split_children:
                             #   split_children.append(parent)
                    if split_child not in split_children:
                        split_children.append(split_child)

            for link in links:
                # don't think I need any of this
                # str_link = str(link)
                # split_link = str_link.split('/')
                # split_link.remove('')
                # split_link.remove('2015')
                # split_link.remove('Volume1')
                # if 'default.htm' in str_link:
                #     split_link.remove('default.htm')

                if ('/' + id + '/') in str(link):
                    next_link = response.urljoin(link)
                    yield scrapy.Request(next_link, callback=self.parse)

        outfile = open('outfile.txt', 'w')
        sorted_children = sorted(split_children)
        for child in sorted_children:
            outfile.write(str(child) + '\n')








