from dataclasses import dataclass

from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas, CanvasResult


@dataclass
class Node:
    x: int
    y: int

    def __iter__(self):
        yield from [self.x, self.y]


@dataclass
class ROI:
    nodes: list[Node]


def get_ROIs(self) -> list[ROI]:
    rois = [ROI([Node(*v[1:]) for v in obj['path'][:-1]])
            for obj in self.json_data['objects']]
    return rois


def update_ROIs(self, rois: list[ROI]):
    for i_roi, roi in enumerate(rois):
        for i_node, node in enumerate(roi.nodes):
            self.json_data['objects'][i_roi]['path'][i_node][1:] = list(node)


def get_fill_color(self, i):
    return self.json_data['objects'][i]['fill'].removesuffix('30')


def set_fill_color(self, i, color):
    self.json_data['objects'][i]['fill'] = f'{color}30'


def setup():
    if not hasattr(CanvasResult, 'get_ROIs'):
        setattr(CanvasResult, 'get_ROIs', get_ROIs)

    if not hasattr(CanvasResult, 'update_ROIs'):
        setattr(CanvasResult, 'update_ROIs', update_ROIs)

    if not hasattr(CanvasResult, 'get_fill_color'):
        setattr(CanvasResult, 'get_fill_color', get_fill_color)

    if not hasattr(CanvasResult, 'set_fill_color'):
        setattr(CanvasResult, 'set_fill_color', set_fill_color)

    if 'canvas_result' not in st.session_state:
        st.session_state['canvas_result'] = CanvasResult()


if __name__ == '__main__':
    setup()

    if img := st.file_uploader('Upload image.', type=['png', 'jpg']):
        bg_image = Image.open(img)
        canvas_result = st_canvas(
            fill_color='#ff000020',
            stroke_width=1,
            background_image=bg_image,
            height=bg_image.height,
            width=bg_image.width,
            drawing_mode='polygon',
            initial_drawing=st.session_state['canvas_result'].json_data
        )

        if canvas_result.json_data and all([obj['type'] == 'path' for obj in canvas_result.json_data['objects']]):
            rois = canvas_result.get_ROIs()

            with st.sidebar:
                with st.form('roi_setting'):
                    applied = st.form_submit_button('Apply')

                    for i_roi, roi in enumerate(rois):
                        st.header(f'ROI: {i_roi}')

                        c, d = st.columns(2)
                        color = c.color_picker(
                            'Fill color', canvas_result.get_fill_color(i_roi), key=f'cp_{i_roi}')
                        canvas_result.set_fill_color(i_roi, color)

                        if d.form_submit_button(f'Delete(ROI{i_roi})'):
                            canvas_result.json_data['objects'].pop(i_roi)
                            st.session_state['canvas_result'] = canvas_result
                            st.experimental_rerun()

                        left, right = st.columns(2)
                        with left:
                            st.write(f'x(0~{bg_image.width})')
                        with right:
                            st.write(f'y(0~{bg_image.height})')

                        for i_node, node in enumerate(roi.nodes):
                            with left:
                                x = st.number_input(f'Node: {i_node}', 0,
                                                    bg_image.width, node.x, key=f'num_{i_roi}{i_node}x')
                            with right:
                                y = st.number_input('', 0,
                                                    bg_image.height, node.y, key=f'num_{i_roi}{i_node}y')
                            rois[i_roi].nodes[i_node] = Node(x, y)

                    if applied:
                        canvas_result.update_ROIs(rois)
                        st.session_state['canvas_result'] = canvas_result
                        st.experimental_rerun()

            for roi in rois:
                st.write(roi)
                st.write(sum([list(node) for node in roi.nodes], []))
