package TriangleClass; // 根据您的项目结构，包名可能是 TriangleClass

import soot.*;
import soot.jimple.toolkits.callgraph.CHATransformer;
import soot.options.Options;
import soot.toolkits.graph.BriefUnitGraph;
import soot.toolkits.graph.UnitGraph;
import soot.util.cfgcmd.CFGToDotGraph;
import soot.util.dot.DotGraph;

import java.io.File;
import java.util.Collections;

public class GenerateCFG {

    public static void main(String[] args) {
        // 设置 Soot 的类路径，指向您的项目编译后的类文件
        String userDir = System.getProperty("user.dir");
        String classPath = userDir + File.separator + "target" + File.separator + "classes";
        Options.v().set_soot_classpath(classPath);

        // 设置输入目录或文件
        Options.v().set_process_dir(Collections.singletonList(classPath));

        // 允许 phantom references
        Options.v().set_allow_phantom_refs(true);

        // 应用 CHA 转换，构建调用图 (可选，但对于更复杂的程序可能有用)
        CHATransformer.v().transform();

        // 获取要分析的类
        String targetClassName = "TriangleClass.Triangle"; // 根据您的实际类名修改
        SootClass c = Scene.v().getSootClass(targetClassName);
        c.setApplicationClass();

        // 指定输出目录
        String outputDir = "C:" + File.separator + "Users" + File.separator + "qiqi" + File.separator + "OneDrive" + File.separator + "Desktop" + File.separator + "code" + File.separator + "software_testing" + File.separator + "t1" + File.separator + "t2_1" + File.separator + "pic";

        // 创建输出目录，如果不存在
        File dir = new File(outputDir);
        if (!dir.exists()) {
            if (dir.mkdirs()) {
                System.out.println("成功创建输出目录: " + outputDir);
            } else {
                System.err.println("创建输出目录失败: " + outputDir);
            }
        } else {
            System.out.println("输出目录已存在: " + outputDir);
        }

        // 遍历所有的方法并生成控制流图
        for (SootMethod method : c.getMethods()) {
            Body b = method.retrieveActiveBody();
            UnitGraph graph = new BriefUnitGraph(b);

            // 设置输出文件名
            String outputFileName = "cfg_" + method.getName();
            String outputFile = outputDir + File.separator + outputFileName + ".dot";

            System.out.println("正在处理方法: " + method.getName());
            System.out.println("尝试写入文件: " + outputFile);

            // 创建 CFGToDotGraph 对象
            CFGToDotGraph cfgToDot = new CFGToDotGraph();

            // 生成 DotGraph 对象
            DotGraph dotGraph = cfgToDot.drawCFG(graph, b);

            // 将 DotGraph 写入文件到指定的目录
            dotGraph.plot(outputFile);

            System.out.println("文件写入完成: " + outputFile);
        }

        System.out.println("控制流图生成完成！");
    }
}