import os
import re


class M3uParser:
    def __init__(self):
        self.files = []

    # Read the file from the given path
    def read_m3u(self, file_path):
        file = open(file_path)
        self.load_content(file.read())

    def load_content(self, content):
        lines = []
        for line in content.split('\n'):
            ln = line.rstrip()
            if ln:
                lines.append(ln)
        self.lines = lines
        return len(self.lines)

    def parse(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == '#':
                # print("Letto carattere interessante")
                self._manage_line(n)

    # Getter for the list
    def get_list(self):
        return self.files

    # Return the info assciated to a certain file name
    def get_custom_title(self, original_name):
        result = list(filter(lambda file: file['titleFile'] == original_name, self.files))
        if len(result):
            return result
        else:
            print('No file corresponding to: ' + original_name)

    # Remove files with a certain file extension
    def filter_out_files_ending_with(self, extension):
        self.files = list(filter(lambda file: not file['titleFile'].endswith(extension), self.files))

    # Select only files with a certain file extension
    def filter_in_files_ending_with(self, extension):
        # Use the extension as list
        if not isinstance(extension, list):
            extension = [extension]
        if not len(extension):
            return
        new = []
        # Iterate over all files and extensions
        for file in self.files:
            for ext in extension:
                if file['titleFile'].endswith(ext):
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.files = new

    # Remove files that contains a certain filterWord
    def filter_out_files_of_groups_containing(self, filter_word):
        self.files = list(filter(lambda file: filter_word not in file['tvg-group'], self.files))

    # Select only files that contais a certain filterWord
    def filter_in_files_of_groups_containing(self, filter_word):
        # Use the filter words as list
        if not isinstance(filter_word, list):
            filter_word = [filter_word]
        if not len(filter_word):
            return
        new = []
        for file in self.files:
            for fw in filter_word:
                if fw in file['tvg-group']:
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.files = new

    # private
    def _manage_line(self, n):
        line_info = self.lines[n]
        line_link = self.lines[n + 1]
        if line_info != "#EXTM3U":
            m = re.search("tvg-name=\"(.*?)\"", line_info)
            name = m.group(1) if m else 'Unknown'
            m = re.search("tvg-ID=\"(.*?)\"", line_info)
            id = m.group(1) if m else 'Unknown'
            m = re.search("tvg-logo=\"(.*?)\"", line_info)
            logo = m.group(1) if m else 'Unknown'
            m = re.search("group-title=\"(.*?)\"", line_info)
            group = m.group(1) if m else 'Unknown'
            m = re.search("[,](?!.*[,])(.*?)$", line_info)
            title = m.group(1) if m else 'Unknown'
            # ~ print(name+"||"+id+"||"+logo+"||"+group+"||"+title)

            test = {
                'title': title,
                'tvg-name': name,
                'tvg-ID': id,
                'tvg-logo': logo,
                'tvg-group': group,
                'titleFile': os.path.basename(line_link),
                'link': line_link
            }
            self.files.append(test)
