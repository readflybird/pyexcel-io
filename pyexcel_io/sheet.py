"""
    pyexcel_io.sheet
    ~~~~~~~~~~~~~~~~~~~

    The io interface to file extensions

    :copyright: (c) 2014-2016 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from pyexcel_io._compact import irange
from pyexcel_io.utils import _index_filter
import pyexcel_io.constants as constants


class NamedContent:
    """
    Helper class for content that does not have a name
    """

    def __init__(self, name, payload):
        self.name = name
        self.payload = payload


class SheetReader(object):
    """
    Generic sheet reader
    """
    def __init__(self, sheet,
                 start_row=0, row_limit=-1,
                 start_column=0, column_limit=-1,
                 skip_row_func=None, skip_column_func=None,
                 skip_empty_rows=True, row_renderer=None,
                 **keywords):
        self._native_sheet = sheet
        self._keywords = {}
        self._keywords.update(keywords)
        self._start_row = start_row
        self._row_limit = row_limit
        self._start_column = start_column
        self._column_limit = column_limit
        self._skip_row = _index_filter
        self._skip_column = _index_filter
        self._skip_empty_rows = skip_empty_rows
        self._row_renderer = row_renderer

        if skip_row_func:
            self._skip_row = skip_row_func
        if skip_column_func:
            self._skip_column = skip_column_func

    def to_array(self):
        """2 dimentional representation of the content
        """
        for row_index, row in enumerate(self._iterate_rows()):
            row_position = self._skip_row(
                row_index, self._start_row, self._row_limit)
            if row_position == constants.SKIP_DATA:
                continue
            elif row_position == constants.STOP_ITERATION:
                break

            return_row = []
            tmp_row = []

            for column_index, cell_value in enumerate(
                    self._iterate_columns(row)):
                column_position = self._skip_column(
                    column_index, self._start_column, self._column_limit)
                if column_position == constants.SKIP_DATA:
                    continue
                elif column_position == constants.STOP_ITERATION:
                    break

                tmp_row.append(cell_value)
                if cell_value is not None and cell_value != '':
                    return_row += tmp_row
                    tmp_row = []
            if self._skip_empty_rows:
                if len(return_row) < 1:
                    # we by-pass next yeild here
                    # because it is an empty row
                    continue

            if self._row_renderer:
                return_row = self._row_renderer(return_row)
            yield return_row

    def _iterate_rows(self):
        return irange(self.number_of_rows())

    def _iterate_columns(self, row):
        for column in irange(self.number_of_columns()):
            yield self._cell_value(row, column)

    def _cell_value(self, row, column):
        """
        implement this method if the customer driver
        provides random access
        """
        raise NotImplementedError("Please implement to_array()")


class SheetWriter(object):
    """
    Generic sheet writer
    """

    def __init__(self, native_book, native_sheet, name, **keywords):
        if name:
            sheet_name = name
        else:
            sheet_name = constants.DEFAULT_SHEET_NAME
        self._native_book = native_book
        self._native_sheet = native_sheet
        self._keywords = keywords
        self.set_sheet_name(sheet_name)

    def set_sheet_name(self, name):
        """
        Set sheet name
        """
        pass

    def write_row(self, array):
        """
        write a row into the file
        """
        raise NotImplementedError("Please implement write_row")

    def write_array(self, table):
        """
        For standalone usage, write an array
        """
        for row in table:
            self.write_row(row)

    def close(self):
        """
        This call actually save the file
        """
        pass
